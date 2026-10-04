import time
import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.config import CATALOG_DB_PATH
from src.models import (
    CommerceIntent, ProductItem, UCPCheckoutPayload, SafetyCheckResult, PipelineResponse
)
from src.ucp_tools import UCPCommerceEngine
from src.arbiter import MonetizationGuardrail
from src.engine import LocalLLMEngine

class ShopStreamPipeline:
    """Orchestrator for the ShopStream-Copilot in-stream commerce pipeline.
    Executes context retrieval, intent parsing, safety guardrails, UCP tool calling,
    and response synthesis with low-latency telemetry logging."""

    def __init__(
        self,
        ucp_engine: Optional[UCPCommerceEngine] = None,
        guardrail: Optional[MonetizationGuardrail] = None,
        llm_engine: Optional[LocalLLMEngine] = None,
        db_path: Path = CATALOG_DB_PATH
    ):
        self.db_path = db_path
        self.ucp_engine = ucp_engine or UCPCommerceEngine(db_path=self.db_path)
        self.guardrail = guardrail or MonetizationGuardrail(db_path=self.db_path)
        self.llm_engine = llm_engine or LocalLLMEngine()

    def _get_creator_id(self, video_id: str) -> str:
        """Lookup creator ID from video metadata table."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT creator_id FROM video_metadata WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row["creator_id"]
        except Exception:
            pass
        return "creator_zurich_default"

    def process_viewer_request(
        self,
        video_id: str,
        timestamp_sec: float,
        user_query: str,
        user_id: str = "usr_yt_zurich_882",
        user_context: Optional[Dict[str, Any]] = None
    ) -> PipelineResponse:
        """Process viewer query through the complete ShopStream pipeline.
        
        Args:
            video_id: Active YouTube video ID.
            timestamp_sec: Current video playback position.
            user_query: Viewer text prompt or chat message.
            user_id: Viewer user ID.
            user_context: Additional user preferences or hardware specs for compatibility validation.
            
        Returns:
            PipelineResponse Pydantic schema containing intent, safety, products, checkout, and telemetry.
        """
        start_total = time.perf_counter()
        latencies: Dict[str, float] = {}
        ucp_logs: List[Dict[str, Any]] = []

        # 1. Retrieve Active Transcript Context
        cue = self.guardrail.get_active_transcript_cue(video_id, timestamp_sec)
        active_transcript_text = cue["text"] if cue else ""

        # 2. Safety Check (MonetizationGuardrail)
        start_safety = time.perf_counter()
        safety: SafetyCheckResult = self.guardrail.check_monetization_safety(video_id, timestamp_sec)
        latencies["guardrail_ms"] = round((time.perf_counter() - start_safety) * 1000, 2)

        # 3. Intent Parsing (LocalLLMEngine / Mock)
        start_intent = time.perf_counter()
        intent: CommerceIntent = self.llm_engine.parse_intent(user_query, active_transcript_text)
        latencies["intent_ms"] = round((time.perf_counter() - start_intent) * 1000, 2)

        products: List[ProductItem] = []
        checkout_payload: Optional[UCPCheckoutPayload] = None

        # Handle Guardrail Safety Suppression
        if not safety.is_safe_to_monetize:
            ucp_logs.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "event": "UCP_GUARDRAIL_SUPPRESSION",
                "reason": safety.reason,
                "sensitive_tags": safety.sensitive_tags
            })
            start_synth = time.perf_counter()
            response_text = self.llm_engine.synthesize_response(user_query, [], safety, None, active_transcript_text)
            latencies["synthesis_ms"] = round((time.perf_counter() - start_synth) * 1000, 2)
            latencies["total_ms"] = round((time.perf_counter() - start_total) * 1000, 2)

            return PipelineResponse(
                intent=intent,
                safety=safety,
                products=[],
                checkout_payload=None,
                response_text=response_text,
                latency_ms=latencies,
                ucp_logs=ucp_logs
            )

        # 4. UCP Tool Execution for Commercial Intent
        start_tool = time.perf_counter()
        if intent.is_commercial:
            # Step 4a: Product Search or Direct Resolution
            if intent.extracted_sku:
                prod = self.ucp_engine.get_product_details(intent.extracted_sku)
                if prod:
                    products.append(prod)
                    ucp_logs.append({
                        "timestamp": time.strftime("%H:%M:%S"),
                        "event": "UCP_TOOL_SKU_LOOKUP",
                        "sku_id": intent.extracted_sku,
                        "title": prod.title
                    })

            if not products and cue and cue.get("featured_skus"):
                for sku in cue["featured_skus"]:
                    prod = self.ucp_engine.get_product_details(sku)
                    if prod:
                        products.append(prod)

            if not products:
                search_q = intent.search_query or intent.user_query
                products = self.ucp_engine.search_catalog(query=search_q, max_results=3)
                ucp_logs.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "event": "UCP_TOOL_CATALOG_SEARCH",
                    "query": search_q,
                    "results_count": len(products)
                })

            # Step 4b: Compatibility Check if requested
            if intent.intent_type == "compatibility_check" and products:
                compat_res = self.ucp_engine.validate_compatibility(products[0].sku_id, user_context or {})
                ucp_logs.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "event": "UCP_TOOL_COMPATIBILITY_CHECK",
                    "result": compat_res
                })

            # Step 4c: Execute 1-Click Google Pay Checkout if requested
            if intent.intent_type == "checkout_request" and products:
                target_sku = products[0].sku_id
                creator_id = self._get_creator_id(video_id)
                checkout_payload = self.ucp_engine.create_checkout_session(
                    sku_id=target_sku,
                    user_id=user_id,
                    creator_id=creator_id
                )
                ucp_logs.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "event": "UCP_TOOL_CHECKOUT_SESSION_CREATED",
                    "transaction_id": checkout_payload.transaction_id,
                    "sku_id": checkout_payload.sku_id,
                    "total_amount": checkout_payload.total_amount,
                    "creator_commission": checkout_payload.creator_commission_amount
                })

        latencies["tool_ms"] = round((time.perf_counter() - start_tool) * 1000, 2)

        # 5. Synthesis
        start_synth = time.perf_counter()
        response_text = self.llm_engine.synthesize_response(user_query, products, safety, checkout_payload, active_transcript_text)
        latencies["synthesis_ms"] = round((time.perf_counter() - start_synth) * 1000, 2)
        latencies["total_ms"] = round((time.perf_counter() - start_total) * 1000, 2)

        return PipelineResponse(
            intent=intent,
            safety=safety,
            products=products,
            checkout_payload=checkout_payload,
            response_text=response_text,
            latency_ms=latencies,
            ucp_logs=ucp_logs
        )
