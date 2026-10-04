import pytest
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.pipeline import ShopStreamPipeline
from src.models import PipelineResponse

@pytest.fixture
def pipeline():
    return ShopStreamPipeline()

def test_pipeline_commercial_query(pipeline):
    """Test full pipeline processing for commercial product inquiry."""
    res = pipeline.process_viewer_request(
        video_id="vid_sony_alpha",
        timestamp_sec=20.0,
        user_query="Tell me about the Sony 24-70mm lens"
    )
    assert isinstance(res, PipelineResponse)
    assert res.intent.is_commercial is True
    assert res.safety.is_safe_to_monetize is True
    assert len(res.products) > 0
    assert "total_ms" in res.latency_ms

def test_pipeline_safety_suppression(pipeline):
    """Test pipeline suppresses commerce calls during crisis video segment."""
    res = pipeline.process_viewer_request(
        video_id="vid_earthquake_news",
        timestamp_sec=50.0,
        user_query="Where can I buy emergency equipment?"
    )
    assert isinstance(res, PipelineResponse)
    assert res.safety.is_safe_to_monetize is False
    assert len(res.products) == 0
    assert res.checkout_payload is None
    assert "Safety Guardrail Active" in res.response_text
    assert any(log["event"] == "UCP_GUARDRAIL_SUPPRESSION" for log in res.ucp_logs)

def test_pipeline_checkout_request(pipeline):
    """Test pipeline processes instant 1-click Google Pay checkout session."""
    res = pipeline.process_viewer_request(
        video_id="vid_pro_gaming",
        timestamp_sec=60.0,
        user_query="Order the Keychron Q1 Pro keyboard right now with 1-click",
        user_id="usr_test_buyer_99"
    )
    assert isinstance(res, PipelineResponse)
    assert res.intent.intent_type == "checkout_request"
    assert res.checkout_payload is not None
    assert res.checkout_payload.payment_status == "SUCCESS"
    assert res.checkout_payload.transaction_id.startswith("ucp_tx_")
    assert any(log["event"] == "UCP_TOOL_CHECKOUT_SESSION_CREATED" for log in res.ucp_logs)
