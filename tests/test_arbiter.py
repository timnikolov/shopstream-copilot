import pytest
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.arbiter import MonetizationGuardrail
from src.models import SafetyCheckResult

@pytest.fixture
def guardrail():
    return MonetizationGuardrail()

def test_safe_segment_monetization(guardrail):
    """Test safe video segment permits monetization."""
    result = guardrail.check_monetization_safety(video_id="vid_sony_alpha", timestamp_sec=20.0)
    assert isinstance(result, SafetyCheckResult)
    assert result.is_safe_to_monetize is True
    assert result.reason is None
    assert len(result.sensitive_tags) == 0

def test_sensitive_segment_suppression(guardrail):
    """Test sensitive crisis segment suppresses monetization."""
    result = guardrail.check_monetization_safety(video_id="vid_earthquake_news", timestamp_sec=45.0)
    assert isinstance(result, SafetyCheckResult)
    assert result.is_safe_to_monetize is False
    assert result.reason is not None
    assert "disaster" in result.sensitive_tags or "tragedy" in result.sensitive_tags

def test_transcript_override_keyword_detection(guardrail):
    """Test real-time keyword trigger in transcript string override."""
    sensitive_text = "Emergency hospital evacuations are taking place following the fatal explosion."
    result = guardrail.check_monetization_safety(video_id="vid_sony_alpha", timestamp_sec=10.0, transcript_override=sensitive_text)
    assert result.is_safe_to_monetize is False
    assert any(tag in ["emergency", "hospital", "fatal", "evacuation"] for tag in result.sensitive_tags)
