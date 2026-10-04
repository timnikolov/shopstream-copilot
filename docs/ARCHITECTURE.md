# System Architecture Specification
## ShopStream-Copilot Technical Blueprint & UCP Data Flow
**Systems Domain:** In-Stream Video Commerce & Platform Monetization Systems  
**Document ID:** ARCH-2026-SSC-003  

---

## 1. High-Level Architecture Diagram

```
                             ┌─────────────────────────────────┐
                             │       Streamlit UI Surface      │
                             │  (YouTube Watch & Shop Surface) │
                             └────────────────┬────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │       ShopStreamPipeline        │
                             │  (Orchestrator & Telemetry)     │
                             └───────┬─────────────────┬───────┘
                                     │                 │
            ┌────────────────────────┴──┐           ┌──┴────────────────────────┐
            ▼                           ▼           ▼                           ▼
┌───────────────────────────┐ ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   MonetizationGuardrail   │ │  LocalLLMEngine   │ │ UCPCommerceEngine │ │ SQLite Catalog DB │
│ (Google Ads Safety Check) │ │ (LM Studio / Mock)│ │ (Google Pay Tool) │ │ (50+ SKUs / Cues) │
└───────────────────────────┘ └───────────────────┘ └───────────────────┘ └───────────────────┘
```

---

## 2. Component Technical Breakdown

### 2.1 `ShopStreamPipeline` (`src/pipeline.py`)
Central execution harness coordinating query ingestion, timestamp synchronization, safety filtering, catalog tool invocation, and low-latency payload generation.

### 2.2 `MonetizationGuardrail` (`src/arbiter.py`)
Enforces Google Ads & Creator Brand Safety policies. Inspects timestamped transcript cues for sensitive keywords (`disaster`, `bereavement`, `emergency`, `medical_crisis`). Returns `SafetyCheckResult` with safety flag and score.

### 2.3 `LocalLLMEngine` & `MockLMEngine` (`src/engine.py`)
OpenAI-compatible client targeting LM Studio at `http://localhost:1234/v1`. If LM Studio is unreachable or no model is loaded, automatically switches to `MockLMEngine` for zero-downtime execution.

### 2.4 `UCPCommerceEngine` (`src/ucp_tools.py`)
Universal Commerce Protocol (UCP) function calling engine. Interfaces with `data/catalog.db` SQLite schema to execute `search_catalog`, `get_product_details`, `validate_compatibility`, and `create_checkout_session`.

---

## 3. Universal Commerce Protocol (UCP) API Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UCPCheckoutPayload",
  "type": "object",
  "properties": {
    "transaction_id": { "type": "string" },
    "sku_id": { "type": "string" },
    "total_amount": { "type": "number" },
    "creator_id": { "type": "string" },
    "payment_status": { "type": "string", "enum": ["SUCCESS", "PENDING", "FAILED"] },
    "confirmation_token": { "type": "string" },
    "creator_commission_amount": { "type": "number" },
    "timestamp": { "type": "string", "format": "date-time" }
  },
  "required": ["transaction_id", "sku_id", "total_amount", "creator_id", "payment_status", "confirmation_token"]
}
```
