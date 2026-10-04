import sqlite3
import re
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.config import CATALOG_DB_PATH, SENSITIVE_TAGS
from src.models import SafetyCheckResult

class MonetizationGuardrail:
    """MonetizationGuardrail enforces Google Ads Brand Safety & Creator Policy standards.
    It inspects timestamped video transcripts for sensitive topic cues (e.g. disasters, self-harm,
    tragedy, medical emergencies, political violence) and suppresses commerce overlays when active."""

    def __init__(self, db_path: Path = CATALOG_DB_PATH):
        self.db_path = db_path
        # Non-capturing regex pattern matching sensitive topics in real-time transcript text
        self.sensitive_keywords = [
            r"\bearthquake\b", r"\bdisaster\b", r"\bcasualt(?:y|ies)\b", r"\bfatal(?:ity|ities)?\b",
            r"\bemergency\b", r"\bhospital\b", r"\btragedy\b", r"\bgrief\b", r"\bdeath\b",
            r"\bshooting\b", r"\bwar\b", r"\bconflict\b", r"\bsuicide\b", r"\bself-harm\b",
            r"\bcrisis\b", r"\bviolence\b", r"\bevacuation\b"
        ]
        self.keyword_regex = re.compile("|".join(self.sensitive_keywords), re.IGNORECASE)

    def _get_connection(self) -> sqlite3.Connection:
        """Establish connection to catalog database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_active_transcript_cue(self, video_id: str, timestamp_sec: float) -> Optional[Dict[str, Any]]:
        """Retrieve the transcript cue active at a specific video timestamp."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp_start, timestamp_end, speaker, text, sensitive_tag, featured_skus_json
            FROM video_transcripts
            WHERE video_id = ? AND ? >= timestamp_start AND ? <= timestamp_end
            ORDER BY timestamp_start ASC
            LIMIT 1
        """, (video_id, timestamp_sec, timestamp_sec))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "timestamp_start": float(row["timestamp_start"]),
            "timestamp_end": float(row["timestamp_end"]),
            "speaker": row["speaker"],
            "text": row["text"],
            "sensitive_tag": row["sensitive_tag"],
            "featured_skus": json.loads(row["featured_skus_json"]) if row["featured_skus_json"] else []
        }

    def check_monetization_safety(
        self, 
        video_id: str, 
        timestamp_sec: float, 
        transcript_override: Optional[str] = None
    ) -> SafetyCheckResult:
        """Evaluate brand safety policy compliance for a given video segment.
        
        Args:
            video_id: YouTube video ID.
            timestamp_sec: Playback timestamp in seconds.
            transcript_override: Optional explicit transcript text string to evaluate.
            
        Returns:
            SafetyCheckResult Pydantic schema detailing whether monetization is permitted.
        """
        detected_tags: List[str] = []
        reasons: List[str] = []

        # 1. Lookup transcript cue from DB if available
        cue = self.get_active_transcript_cue(video_id, timestamp_sec)
        text_to_analyze = transcript_override or (cue["text"] if cue else "")

        # 2. Check metadata tag from database cue
        if cue and cue.get("sensitive_tag"):
            tag = cue["sensitive_tag"]
            if tag in SENSITIVE_TAGS or tag != "":
                detected_tags.append(tag)
                reasons.append(f"Database policy tag trigger: '{tag}' active at {timestamp_sec:.1f}s.")

        # 3. Perform real-time NLP/Regex keyword detection on active spoken transcript text
        if text_to_analyze:
            matches = self.keyword_regex.findall(text_to_analyze)
            if matches:
                matched_words = list(set([m.lower() for m in matches if isinstance(m, str)]))
                for word in matched_words:
                    if word not in detected_tags:
                        detected_tags.append(word)
                reasons.append(f"Spoken text sensitive keywords detected: {', '.join(matched_words)}")

        # 4. Synthesize decision
        if detected_tags:
            risk_score = min(1.0, 0.70 + (0.15 * len(detected_tags)))
            reason_str = " | ".join(reasons)
            return SafetyCheckResult(
                is_safe_to_monetize=False,
                reason=f"Monetization suppressed due to sensitive topic: {reason_str}",
                sensitive_tags=detected_tags,
                risk_score=risk_score
            )

        return SafetyCheckResult(
            is_safe_to_monetize=True,
            reason=None,
            sensitive_tags=[],
            risk_score=0.02
        )
