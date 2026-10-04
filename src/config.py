import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

# Database & Data Paths
CATALOG_DB_PATH = DATA_DIR / "catalog.db"
TRANSCRIPTS_JSON_PATH = DATA_DIR / "video_transcripts.json"

# LM Studio & LLM Settings (Use 127.0.0.1 to avoid macOS mDNS resolution delays)
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "lmstudio-community/qwen2.5-7b-instruct")
DEFAULT_TEMPERATURE = 0.1
MAX_TOKENS = 512

# Guardrail Policies
SAFETY_POLICY_VERSION = "2026.1-YTS-ZURICH"
SENSITIVE_TAGS = [
    "self_harm",
    "bereavement",
    "disaster",
    "violence",
    "medical_emergency",
    "political_controversy",
    "tragedy",
    "war_conflict",
    "hate_speech",
]

# UCP Commerce Defaults
DEFAULT_CURRENCY = "USD"
GOOGLE_PAY_MERCHANT_ID = "gpay_merchant_yt_shopstream_zurich_8891"
DEFAULT_COMMISSION_RATE = 0.08  # 8% default creator affiliate split

# A/B Experimentation Defaults
CONTROL_VARIANT_ID = "control_static_links"
EXPERIMENT_VARIANT_ID = "variant_shopstream_copilot"
