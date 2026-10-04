import json
import logging
import requests
from typing import List, Optional, Dict, Any

from src.config import LM_STUDIO_URL, DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE
from src.models import CommerceIntent, ProductItem, SafetyCheckResult, UCPCheckoutPayload

logger = logging.getLogger(__name__)

class MockLMEngine:
    """Mock LLM Engine providing structured intent extraction and conversational synthesis
    when LM Studio (http://localhost:1234/v1) is unreachable or inactive."""

    def parse_intent(self, user_query: str, active_transcript: str = "") -> CommerceIntent:
        """Parse viewer intent using rule-based NLP heuristic fallback."""
        query_lower = user_query.lower()

        # Action keywords
        is_checkout = any(k in query_lower for k in ["buy", "purchase", "checkout", "order", "get this", "1-click"])
        is_compat = any(k in query_lower for k in ["compatible", "fit", "mount", "work with", "size", "match", "true to size", "good for"])
        is_price = any(k in query_lower for k in ["price", "cost", "how much", "cheap", "expensive", "discount"])
        
        # Product interest keywords
        commercial_keywords = [
            "what", "specs", "details", "tell me", "review", "feature", "recommend",
            "camera", "lens", "coat", "boots", "chair", "keyboard", "serum", "toner",
            "tripod", "mic", "microphone", "monitor", "headset", "mouse", "scarf",
            "sweater", "bag", "blazer", "exfoliant", "cream", "supplies", "bha",
            "snail", "mucin", "airwrap", "peak design", "rode", "sony", "dr. martens",
            "acne", "keychron", "sol de janeiro", "dyson", "cosrx", "paula", "anua"
        ]
        
        is_inquiry = any(k in query_lower for k in commercial_keywords)

        # Non-commercial question check
        non_commercial_triggers = ["city", "recorded in", "month", "where is", "who is", "weather", "located"]
        is_explicit_non_commercial = any(k in query_lower for k in non_commercial_triggers) and not any(k in query_lower for k in ["buy", "cost", "price", "order"])

        is_commercial = (is_checkout or is_compat or is_price or is_inquiry) and not is_explicit_non_commercial

        intent_type = "general_qa"
        if is_commercial:
            if is_checkout:
                intent_type = "checkout_request"
            elif is_compat:
                intent_type = "compatibility_check"
            elif is_price:
                intent_type = "price_check"
            elif is_inquiry:
                intent_type = "product_inquiry"

        confidence = 0.95 if is_commercial else (0.90 if is_explicit_non_commercial else 0.50)

        # Extract explicit SKU or item search query keyword
        search_query = user_query
        extracted_sku = None

        if "tripod" in query_lower or "peak design" in query_lower:
            extracted_sku = "SKU-PEAK-TRIPOD-CF"
            search_query = "Peak Design Travel Tripod"
        elif "24-70" in query_lower or "gm ii" in query_lower:
            extracted_sku = "SKU-SONY-2470GM2"
            search_query = "Sony FE 24-70mm GM II lens"
        elif "a7iv" in query_lower or "camera" in query_lower or "alpha" in query_lower:
            extracted_sku = "SKU-SONY-A7IV"
            search_query = "Sony Alpha 7 IV"
        elif "trench" in query_lower or "acne" in query_lower:
            extracted_sku = "SKU-ACNE-TRENCH-BRN"
            search_query = "Acne Studios Trench Coat"
        elif "boot" in query_lower or "doc" in query_lower or "martens" in query_lower:
            extracted_sku = "SKU-DRM-1460BOOTS"
            search_query = "Dr. Martens Boots"
        elif "scarf" in query_lower or "toteme" in query_lower:
            extracted_sku = "SKU-TOT-SCARF-BEIGE"
            search_query = "Toteme Wool Scarf"
        elif "monitor" in query_lower or "oled" in query_lower or "lg" in query_lower:
            extracted_sku = "SKU-LG-34OLED"
            search_query = "LG 34 OLED Monitor"
        elif "keyboard" in query_lower or "keychron" in query_lower:
            extracted_sku = "SKU-KEY-Q1PRO"
            search_query = "Keychron Q1 Pro Keyboard"
        elif "snail" in query_lower or "mucin" in query_lower or "cosrx" in query_lower:
            extracted_sku = "SKU-COSRX-SNAIL96"
            search_query = "COSRX Snail Mucin Essence"
        elif "paula" in query_lower or "bha" in query_lower or "exfoliant" in query_lower:
            extracted_sku = "SKU-PAULAS-2BHA"
            search_query = "Paula's Choice 2% BHA Liquid Exfoliant"
        elif "toner" in query_lower or "heartleaf" in query_lower or "anua" in query_lower:
            extracted_sku = "SKU-ANUA-TONER77"
            search_query = "Anua Heartleaf Toner"

        return CommerceIntent(
            is_commercial=is_commercial,
            intent_type=intent_type,
            extracted_sku=extracted_sku,
            confidence=confidence,
            user_query=user_query,
            search_query=search_query
        )

    def synthesize_response(
        self,
        user_query: str,
        products: List[ProductItem],
        safety: SafetyCheckResult,
        checkout: Optional[UCPCheckoutPayload] = None,
        active_transcript: str = ""
    ) -> str:
        """Synthesize natural language response based on products, safety, and checkout results."""
        if not safety.is_safe_to_monetize:
            return f"⚠️ [YouTube Safety Guardrail Active] Commercial features are paused during this segment due to sensitive content policy compliance ({safety.reason})."

        if checkout:
            return f"✅ **Order Confirmed!** Your order for **{checkout.sku_id}** was processed via 1-Click Google Pay (Transaction ID: `{checkout.transaction_id}`). Total: ${checkout.total_amount:.2f}. Creator affiliate earnings of ${checkout.creator_commission_amount:.2f} allocated."

        if products:
            top_p = products[0]
            specs_summary = ", ".join([f"{k}: {v}" for k, v in list(top_p.specs.items())[:3]])
            stock_str = "In Stock" if top_p.in_stock else "Out of Stock"
            return f"The **{top_p.title}** by {top_p.brand} is featured right now for **${top_p.price:.2f} {top_p.currency}** ({stock_str}). Key Specs: {specs_summary}. Tap the UCP Checkout button in the drawer to order instantly with Google Pay!"

        return "I'm monitoring the stream! Ask me about any creator equipment, apparel, or products featured in this video."


class LocalLLMEngine:
    """Local LLM engine interfacing with LM Studio at http://localhost:1234/v1
    with automated fast class-cached health check fallback to MockLMEngine."""

    _cached_availability: Optional[bool] = None

    def __init__(self, base_url: str = LM_STUDIO_URL, model_name: str = DEFAULT_MODEL_NAME):
        self.base_url = base_url
        self.model_name = model_name
        self.mock_engine = MockLMEngine()
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(base_url=self.base_url, api_key="lm-studio")
        return self._client

    def _is_lm_studio_available(self) -> bool:
        """Fast class-cached HTTP GET check to verify LM Studio availability."""
        if LocalLLMEngine._cached_availability is not None:
            return LocalLLMEngine._cached_availability

        try:
            r = requests.get(f"{self.base_url}/models", timeout=0.15)
            if r.status_code == 200:
                data = r.json()
                LocalLLMEngine._cached_availability = bool("data" in data and len(data["data"]) > 0)
            else:
                LocalLLMEngine._cached_availability = False
        except Exception:
            LocalLLMEngine._cached_availability = False

        return LocalLLMEngine._cached_availability

    def parse_intent(self, user_query: str, active_transcript: str = "") -> CommerceIntent:
        """Parse viewer intent via LM Studio structured completion or fallback."""
        if not self._is_lm_studio_available():
            return self.mock_engine.parse_intent(user_query, active_transcript)

        system_prompt = """You are an AI Commerce Intent Parser for YouTube Shopping.
Analyze the user's chat message in the context of the active video transcript.
Output ONLY a JSON object matching this schema:
{
  "is_commercial": bool,
  "intent_type": "product_inquiry" | "compatibility_check" | "price_check" | "checkout_request" | "general_qa",
  "extracted_sku": string | null,
  "confidence": float (0.0 to 1.0),
  "user_query": string,
  "search_query": string | null
}"""

        user_content = f"Active Spoken Transcript: '{active_transcript}'\nViewer Query: '{user_query}'"

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=DEFAULT_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            raw_json = response.choices[0].message.content or "{}"
            data = json.loads(raw_json)
            return CommerceIntent(
                is_commercial=data.get("is_commercial", False),
                intent_type=data.get("intent_type", "general_qa"),
                extracted_sku=data.get("extracted_sku"),
                confidence=float(data.get("confidence", 0.8)),
                user_query=user_query,
                search_query=data.get("search_query", user_query)
            )
        except Exception:
            return self.mock_engine.parse_intent(user_query, active_transcript)

    def synthesize_response(
        self,
        user_query: str,
        products: List[ProductItem],
        safety: SafetyCheckResult,
        checkout: Optional[UCPCheckoutPayload] = None,
        active_transcript: str = ""
    ) -> str:
        """Synthesize response via LM Studio or fallback."""
        if not safety.is_safe_to_monetize:
            return self.mock_engine.synthesize_response(user_query, products, safety, checkout, active_transcript)

        if not self._is_lm_studio_available():
            return self.mock_engine.synthesize_response(user_query, products, safety, checkout, active_transcript)

        products_summary = json.dumps([p.model_dump() for p in products])
        checkout_summary = json.dumps(checkout.model_dump()) if checkout else "None"

        system_prompt = "You are ShopStream-Copilot, an in-stream video shopping assistant for YouTube. Be helpful, concise, and highlight product specs and 1-click Google Pay options."
        user_content = f"Viewer Query: {user_query}\nActive Transcript: {active_transcript}\nFound Products: {products_summary}\nCheckout Token: {checkout_summary}"

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content or self.mock_engine.synthesize_response(user_query, products, safety, checkout, active_transcript)
        except Exception:
            return self.mock_engine.synthesize_response(user_query, products, safety, checkout, active_transcript)
