# Universal Commerce Protocol (UCP v1.2) Specification
## In-Stream Transaction Protocol for Video Commerce
**Standard Organization:** Universal Video Commerce Protocol Consortium  
**Protocol Version:** 1.2.0-STABLE  
**Security Level:** Tokenized PCI-DSS Level 1 / 1-Click Pay End-to-End Encryption  

---

## 1. Protocol Mission & Scope

The **Universal Commerce Protocol (UCP)** is a vendor-neutral, low-latency commerce messaging protocol designed specifically for video streaming surfaces. Unlike standard e-commerce protocols that assume static multi-page navigation (e.g., Cart $\rightarrow$ Shipping $\rightarrow$ Billing $\rightarrow$ Review), UCP executes atomic, context-aware 1-click transactions that complete within the active video frame in under 200 milliseconds.

---

## 2. Core Protocol Lifecyle & Sequence Flow

```
Viewer / Chat            ShopStream Pipeline         MonetizationGuardrail       UCP Commerce Engine        Google Pay Rail
     │                            │                            │                         │                         │
     │── 1. Spoken Cue / Query ──>│                            │                         │                         │
     │                            │── 2. Timestamp Safety ────>│                         │                         │
     │                            │<── 3. Policy Approval ─────│                         │                         │
     │                            │                                                      │                         │
     │                            │── 4. Intent Handshake & Tool Request ───────────────>│                         │
     │                            │<── 5. SKU Details & Compatibility Attestation ───────│                         │
     │                            │                                                      │                         │
     │── 6. 1-Click Buy Intent ──>│                                                      │                         │
     │                            │── 7. create_checkout_session(SKU, Creator, User) ───>│                         │
     │                            │                                                      │── 8. Tokenize GPay ────>│
     │                            │                                                      │<── 9. Auth Token ───────│
     │                            │<── 10. UCPCheckoutPayload (Status: SUCCESS) ─────────│                         │
     │<── 11. In-Stream Receipt ──│                                                                                │
```

---

## 3. Protocol Message Schemas

### 3.1 `UCPHandshakeRequest`
Sent by the client video player upon stream initialization or chapter marker navigation:

```json
{
  "protocol_version": "1.2",
  "client_surface": "youtube_watch_in_stream",
  "video_id": "vid_sony_alpha",
  "playback_timestamp_sec": 20.0,
  "viewer_profile_token": "gpay_tokenized_usr_88291",
  "creator_id": "creator_techvision_88",
  "currency": "USD",
  "locale": "de_CH"
}
```

### 3.2 `UCPCheckoutPayload` (Settlement Schema)
Returned by the UCP Commerce Engine upon successful order tokenization:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UCPCheckoutPayload",
  "type": "object",
  "properties": {
    "transaction_id": {
      "type": "string",
      "pattern": "^ucp_tx_[A-F0-9]{12}$",
      "description": "Cryptographically random unique UCP settlement ID."
    },
    "sku_id": {
      "type": "string",
      "description": "Merchant Center SKU identifier."
    },
    "total_amount": {
      "type": "number",
      "minimum": 0.01,
      "description": "Gross settlement amount in ISO currency."
    },
    "creator_id": {
      "type": "string",
      "description": "Attributed creator ID for affiliate commission allocation."
    },
    "creator_commission_amount": {
      "type": "number",
      "minimum": 0.0,
      "description": "Calculated creator commission split."
    },
    "payment_status": {
      "type": "string",
      "enum": ["SUCCESS", "PENDING", "FAILED"]
    },
    "confirmation_token": {
      "type": "string",
      "pattern": "^gpay_tok_zurich_[a-f0-9]{16}$"
    },
    "payment_method": {
      "type": "string",
      "default": "Google Pay (UCP 1-Click)"
    },
    "shipping_address_hash": {
      "type": "string"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": [
    "transaction_id",
    "sku_id",
    "total_amount",
    "creator_id",
    "payment_status",
    "confirmation_token",
    "creator_commission_amount",
    "timestamp"
  ]
}
```

---

## 4. Standard Protocol Error Codes

| Error Code | HTTP Status | Description & Remediation |
| :--- | :--- | :--- |
| `UCP_ERR_POLICY_SUPPRESSED` | 403 Forbidden | `MonetizationGuardrail` detected sensitive content at current playback timestamp. Shopping overlays must be suppressed. |
| `UCP_ERR_OUT_OF_STOCK` | 409 Conflict | Product SKU inventory count is zero in Merchant Center catalog. Display "Out of Stock" notification. |
| `UCP_ERR_INCOMPATIBLE_CONTEXT` | 422 Unprocessable | Compatibility validator detected hardware or sizing mismatch (e.g. lens mount incompatibility). Prompt viewer for confirmation. |
| `UCP_ERR_TOKEN_EXPIRED` | 401 Unauthorized | Google Pay token expired. Prompt viewer for biometric or security refresh. |
| `UCP_ERR_CREATOR_UNVERIFIED` | 400 Bad Request | Creator channel affiliate split parameters are unconfigured or revoked. |

---

## 5. Security, Fraud Prevention & Privacy

1. **Zero Raw Card Data:** No credit card numbers (PANs) or CVVs traverse the ShopStream pipeline. All payments are processed through tokenized Google Pay virtual account numbers (DPANs).
2. **Deterministic Attribution Lock:** The creator commission split is cryptographically signed at transaction creation, preventing post-purchase attribution hijacking.
3. **Auditing & Webhooks:** Every settlement dispatches asynchronous HMAC-SHA256 signed webhooks to Google Merchant Center and creator analytics dashboards.
