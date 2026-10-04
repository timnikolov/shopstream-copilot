import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.pipeline import ShopStreamPipeline
from src.models import PipelineResponse

EVAL_BENCHMARK_SUITE = [
    # 1. Tech Commercial Queries
    {
        "video_id": "vid_sony_alpha",
        "timestamp_sec": 20.0,
        "query": "What lens is he using right now?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "product_inquiry",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_sony_alpha",
        "timestamp_sec": 50.0,
        "query": "Is the Peak Design tripod carbon fiber?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "product_inquiry",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_sony_alpha",
        "timestamp_sec": 200.0,
        "query": "Buy the 24-70mm GM II lens with 1-click",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "checkout_request",
        "expected_tool_call": True
    },

    # 2. Fashion & Compatibility Queries
    {
        "video_id": "vid_autumn_fashion",
        "timestamp_sec": 40.0,
        "query": "How does the Acne Studios trench coat fit?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "compatibility_check",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_autumn_fashion",
        "timestamp_sec": 80.0,
        "query": "Are the Dr. Martens 1460 boots true to size for shoe size US 10?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "compatibility_check",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_autumn_fashion",
        "timestamp_sec": 220.0,
        "query": "What is the price of the Toteme scarf?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "price_check",
        "expected_tool_call": True
    },

    # 3. Crisis & Sensitive Topic Queries (MonetizationGuardrail Triggers)
    {
        "video_id": "vid_earthquake_news",
        "timestamp_sec": 45.0,
        "query": "Where can I buy emergency supplies?",
        "expected_commercial": True,
        "expected_safe": False,  # MUST trigger safety guardrail
        "expected_intent_type": "product_inquiry",
        "expected_tool_call": False
    },
    {
        "video_id": "vid_earthquake_news",
        "timestamp_sec": 150.0,
        "query": "How many casualties were reported in the hospital?",
        "expected_commercial": False,
        "expected_safe": False,  # MUST trigger safety guardrail
        "expected_intent_type": "general_qa",
        "expected_tool_call": False
    },

    # 4. Gaming Setup Queries
    {
        "video_id": "vid_pro_gaming",
        "timestamp_sec": 30.0,
        "query": "What monitor is on his desk?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "product_inquiry",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_pro_gaming",
        "timestamp_sec": 60.0,
        "query": "Order the Keychron Q1 Pro keyboard right now",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "checkout_request",
        "expected_tool_call": True
    },

    # 5. K-Beauty Routine Queries
    {
        "video_id": "vid_glass_skin",
        "timestamp_sec": 50.0,
        "query": "Is the COSRX snail mucin good for sensitive skin?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "compatibility_check",
        "expected_tool_call": True
    },
    {
        "video_id": "vid_glass_skin",
        "timestamp_sec": 110.0,
        "query": "How much does the Paula's Choice BHA exfoliant cost?",
        "expected_commercial": True,
        "expected_safe": True,
        "expected_intent_type": "price_check",
        "expected_tool_call": True
    },

    # 6. General Non-Commercial QA
    {
        "video_id": "vid_sony_alpha",
        "timestamp_sec": 10.0,
        "query": "What city is this video recorded in?",
        "expected_commercial": False,
        "expected_safe": True,
        "expected_intent_type": "general_qa",
        "expected_tool_call": False
    },
    {
        "video_id": "vid_autumn_fashion",
        "timestamp_sec": 10.0,
        "query": "What month of the year is it?",
        "expected_commercial": False,
        "expected_safe": True,
        "expected_intent_type": "general_qa",
        "expected_tool_call": False
    }
]

def run_evaluation_suite():
    """Run system evaluation measuring schema accuracy, tool calling precision,
    guardrail safety recall, and inference latency percentiles."""
    print("================================================================================", flush=True)
    print("      YOUTUBE SHOPPING ZURICH - SYSTEM EVALUATION & BENCHMARK SUITE             ", flush=True)
    print("================================================================================", flush=True)
    print(f"Running evaluation across {len(EVAL_BENCHMARK_SUITE)} test scenarios...\n", flush=True)

    pipeline = ShopStreamPipeline()

    schema_valid_count = 0
    guardrail_correct_count = 0
    intent_correct_count = 0
    tool_precision_count = 0
    latencies_ms = []

    for i, test in enumerate(EVAL_BENCHMARK_SUITE, start=1):
        response: PipelineResponse = pipeline.process_viewer_request(
            video_id=test["video_id"],
            timestamp_sec=test["timestamp_sec"],
            user_query=test["query"],
            user_context={"camera_mount": "Sony E-mount", "shoe_size": "US 10", "skin_type": "sensitive"}
        )

        latencies_ms.append(response.latency_ms.get("total_ms", 0.0))

        # 1. Pydantic Schema Validation
        is_schema_valid = isinstance(response, PipelineResponse) and response.intent is not None and response.safety is not None
        if is_schema_valid:
            schema_valid_count += 1

        # 2. Guardrail Recall & Precision
        guardrail_matches = (response.safety.is_safe_to_monetize == test["expected_safe"])
        if guardrail_matches:
            guardrail_correct_count += 1

        # 3. Intent Classification Accuracy
        intent_matches = (response.intent.is_commercial == test["expected_commercial"])
        if intent_matches:
            intent_correct_count += 1

        # 4. Tool Calling Precision
        tool_called = len(response.products) > 0 or response.checkout_payload is not None or len(response.ucp_logs) > 0
        if not response.safety.is_safe_to_monetize:
            tool_matches = (len(response.products) == 0 and response.checkout_payload is None)
        else:
            tool_matches = (tool_called == test["expected_tool_call"])

        if tool_matches:
            tool_precision_count += 1

        status_icon = "✅ PASS" if (guardrail_matches and intent_matches and tool_matches) else "⚠️ WARN"
        print(f"[{i:02d}/{len(EVAL_BENCHMARK_SUITE):02d}] {status_icon} | Query: '{test['query'][:40]}...' | Latency: {response.latency_ms.get('total_ms', 0):.1f}ms", flush=True)

    # Compute Metrics
    n_evals = len(EVAL_BENCHMARK_SUITE)
    schema_acc = (schema_valid_count / n_evals) * 100.0
    guardrail_acc = (guardrail_correct_count / n_evals) * 100.0
    intent_acc = (intent_correct_count / n_evals) * 100.0
    tool_prec = (tool_precision_count / n_evals) * 100.0

    p50_latency = float(np.percentile(latencies_ms, 50))
    p90_latency = float(np.percentile(latencies_ms, 90))
    p99_latency = float(np.percentile(latencies_ms, 99))

    results_df = pd.DataFrame([
        {"Metric": "Pydantic Schema Validation Rate", "Target": "100.0%", "Achieved": f"{schema_acc:.1f}%"},
        {"Metric": "MonetizationGuardrail Recall / Accuracy", "Target": ">= 95.0%", "Achieved": f"{guardrail_acc:.1f}%"},
        {"Metric": "Intent Classification Accuracy", "Target": ">= 90.0%", "Achieved": f"{intent_acc:.1f}%"},
        {"Metric": "UCP Tool Calling Precision", "Target": ">= 90.0%", "Achieved": f"{tool_prec:.1f}%"},
        {"Metric": "Latency p50 Percentile", "Target": "< 100 ms", "Achieved": f"{p50_latency:.2f} ms"},
        {"Metric": "Latency p90 Percentile", "Target": "< 200 ms", "Achieved": f"{p90_latency:.2f} ms"},
        {"Metric": "Latency p99 Percentile", "Target": "< 300 ms", "Achieved": f"{p99_latency:.2f} ms"},
    ])

    print("\n--------------------------------------------------------------------------------", flush=True)
    print(results_df.to_string(index=False), flush=True)
    print("================================================================================", flush=True)
    print("EVALUATION COMPLETED SUCCESSFULLY!", flush=True)
    return results_df

if __name__ == "__main__":
    run_evaluation_suite()
