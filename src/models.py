from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class CommerceIntent(BaseModel):
    """Pydantic schema for parsed viewer commerce intent."""
    is_commercial: bool = Field(
        ..., 
        description="True if viewer query expresses transactional or product interest, False otherwise."
    )
    intent_type: str = Field(
        ..., 
        description="Categorized intent type: product_inquiry, compatibility_check, price_check, checkout_request, general_qa"
    )
    extracted_sku: Optional[str] = Field(
        None, 
        description="Target SKU identifier if specific product was resolved from context."
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score of intent extraction (0.0 to 1.0)."
    )
    user_query: str = Field(
        ..., 
        description="Original raw query submitted by the viewer."
    )
    search_query: Optional[str] = Field(
        None, 
        description="Extracted or normalized product keyword query for catalog search."
    )

class ProductItem(BaseModel):
    """Pydantic schema for catalog product entity from Google Merchant Center."""
    sku_id: str = Field(..., description="Unique product SKU identifier.")
    title: str = Field(..., description="Full descriptive product title.")
    brand: str = Field(..., description="Brand or manufacturer name.")
    price: float = Field(..., gt=0.0, description="Retail price of product.")
    currency: str = Field("USD", description="ISO currency code.")
    in_stock: bool = Field(True, description="Inventory availability flag.")
    specs: Dict[str, Any] = Field(default_factory=dict, description="Structured technical/attribute specifications.")
    creator_commission_rate: float = Field(
        0.08, 
        ge=0.0, 
        le=1.0, 
        description="Creator affiliate commission percentage (e.g. 0.08 for 8%)."
    )
    category: str = Field("General", description="Product catalog category.")
    description: str = Field("", description="Detailed item summary.")
    image_url: Optional[str] = Field(None, description="Product display image URL.")

class UCPCheckoutPayload(BaseModel):
    """Pydantic schema for Universal Commerce Protocol (UCP) 1-click Google Pay transaction payload."""
    transaction_id: str = Field(..., description="Unique UCP checkout transaction ID.")
    sku_id: str = Field(..., description="SKU identifier of purchased item.")
    total_amount: float = Field(..., gt=0.0, description="Final settlement amount in specified currency.")
    creator_id: str = Field(..., description="Channel creator receiving affiliate attribution.")
    payment_status: str = Field(..., description="UCP settlement status (SUCCESS, PENDING, FAILED).")
    confirmation_token: str = Field(..., description="Cryptographic Google Pay token for instant confirmation.")
    creator_commission_amount: float = Field(..., ge=0.0, description="Calculated creator earning for transaction.")
    timestamp: str = Field(..., description="ISO 8601 transaction timestamp.")
    payment_method: str = Field("Google Pay (UCP 1-Click)", description="Tokenized payment rail.")
    shipping_address_hash: str = Field("ucp_tokenized_addr_9984", description="Tokenized customer shipping profile.")

class SafetyCheckResult(BaseModel):
    """Pydantic schema for MonetizationGuardrail safety verification."""
    is_safe_to_monetize: bool = Field(
        ..., 
        description="True if video segment complies with Google Ads safety policies."
    )
    reason: Optional[str] = Field(
        None, 
        description="Explanation if commercial features are suppressed."
    )
    sensitive_tags: List[str] = Field(
        default_factory=list, 
        description="Detected policy violations or sensitive topic tags."
    )
    risk_score: float = Field(
        0.0, 
        ge=0.0, 
        le=1.0, 
        description="Quantitative safety risk assessment score."
    )

class TranscriptCue(BaseModel):
    """Pydantic schema for timestamped video transcript cues."""
    timestamp_start: float = Field(..., ge=0.0, description="Cue start time in seconds.")
    timestamp_end: float = Field(..., ge=0.0, description="Cue end time in seconds.")
    speaker: str = Field("Creator", description="Speaker identifier.")
    text: str = Field(..., description="Spoken transcript snippet.")
    sensitive_tag: Optional[str] = Field(None, description="Associated policy tag if cue touches sensitive topic.")
    featured_skus: List[str] = Field(default_factory=list, description="SKUs featured during this transcript cue.")

class VideoMetadata(BaseModel):
    """Pydantic schema for video container and creator settings."""
    video_id: str = Field(..., description="YouTube video unique ID.")
    title: str = Field(..., description="Video title.")
    channel_name: str = Field(..., description="Creator channel name.")
    creator_id: str = Field(..., description="Creator ID for affiliate splits.")
    duration: float = Field(..., gt=0.0, description="Video total duration in seconds.")
    category: str = Field(..., description="Video category (e.g., Tech, Fashion, News, Gaming, Beauty).")
    transcript_cues: List[TranscriptCue] = Field(default_factory=list, description="Timestamped transcript cues.")
    creator_affiliate_settings: Dict[str, Any] = Field(default_factory=dict, description="Creator commission overrides.")

class PipelineResponse(BaseModel):
    """Pydantic schema for end-to-end ShopStream pipeline execution result."""
    intent: CommerceIntent
    safety: SafetyCheckResult
    products: List[ProductItem] = Field(default_factory=list)
    checkout_payload: Optional[UCPCheckoutPayload] = None
    response_text: str
    latency_ms: Dict[str, float] = Field(default_factory=dict)
    ucp_logs: List[Dict[str, Any]] = Field(default_factory=list)
