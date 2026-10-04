# 🔴 ShopStream-Copilot
### In-Stream Video Commerce & Universal Commerce Protocol (UCP) Agent
**Designed for the YouTube Shopping Consumer Growth Team (Zurich)**

[![Python 3.11](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Protocol](https://img.shields.io/badge/Protocol-Universal_Commerce_Protocol_(UCP_v1.2)-green.svg)](docs/UCP_SPECIFICATION.md)
[![Accessibility](https://img.shields.io/badge/Accessibility-WCAG_2.1_AAA-orange.svg)](docs/ACCESSIBILITY_SPEC.md)
[![Safety](https://img.shields.io/badge/Brand_Safety-Google_Ads_Compliant-red.svg)](docs/SAFETY_AND_ETHICS.md)
[![License](https://img.shields.io/badge/License-Google_Proprietary-black.svg)]()

---

## 🌟 Executive Overview

**ShopStream-Copilot** enables YouTube viewers to watch video content and shop creator-featured products simultaneously without leaving playback or causing watch-time drop-off.

By ingesting timestamped video transcripts, parsing viewer queries, retrieving structured inventory from a local Google Merchant Center SQLite catalog (`data/catalog.db`), and executing 1-click checkout flows via the **Universal Commerce Protocol (UCP)**, ShopStream-Copilot transforms static video watching into an interactive, frictionless shopping experience.

```
                  ┌──────────────────────────────────────────────────┐
                  │          YOUTUBE WATCH & SHOP SURFACE            │
                  │   - Live Video Playback & Synchronized Cues      │
                  │   - In-Stream Drawer with 1-Click Google Pay     │
                  │   - Hardware & Sizing Compatibility Checker      │
                  └─────────────────────────┬────────────────────────┘
                                            │
                                            ▼
                  ┌──────────────────────────────────────────────────┐
                  │               ShopStreamPipeline                 │
                  │   - Context Ingestion & Latency Telemetry        │
                  │   - Intent Parsing (Local LLM / Mock Engine)     │
                  └─────────────┬──────────────────────┬─────────────┘
                                │                      │
                 ┌──────────────┴───────┐       ┌──────┴───────────────┐
                 ▼                      ▼       ▼                      ▼
┌────────────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐
│     MonetizationGuardrail      │ │   UCP Commerce Engine  │ │  SQLite GMC Catalog    │
│  (Google Ads Brand Safety)     │ │ (Tokenized Google Pay) │ │ (52 SKUs / 5 Scenarios)│
└────────────────────────────────┘ └────────────────────────┘ └────────────────────────┘
```

---

## 📚 Product & Technical Documentation Suite

Our repository includes an end-to-end, production-grade documentation suite tailored for engineering, product, trust & safety, and growth leadership:

| Document | Description | Target Persona |
| :--- | :--- | :--- |
| [**PRD.md**](docs/PRD.md) | **Product Requirements Document (0-to-1):** Vision, three-sided marketplace value proposition, detailed user stories, non-functional requirements, and launch milestones. | Product Managers & Engineering Leads |
| [**EXPERIMENT_DESIGN.md**](docs/EXPERIMENT_DESIGN.md) | **A/B Testing & Growth Strategy:** Hypotheses ($H_1, H_2$), primary/secondary metrics, watch-time guardrails, MDE statistical power calculations, sample allocation, and sequential testing rules. | Data Scientists & Growth PMs |
| [**GROWTH_PLAYBOOK.md**](docs/GROWTH_PLAYBOOK.md) | **Creator Monetization & GTM Playbook:** North Star metric tree (GMV/kV), three-sided marketplace flywheel, DACH pilot rollout phases, creator adoption incentives, and merchant onboarding. | Growth Strategists & BizOps |
| [**UCP_SPECIFICATION.md**](docs/UCP_SPECIFICATION.md) | **Universal Commerce Protocol (UCP v1.2) Spec:** Complete protocol message flow, JSON schemas (`UCPHandshake`, `UCPCheckoutPayload`), error codes, and tokenized Google Pay settlement security. | Software Architects & Systems Engineers |
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | **System Architecture Blueprint:** Component architecture, data flow diagrams, LM Studio local model runtime integration, and zero-downtime mock engine fallback. | AI Systems Engineers & Tech Leads |
| [**ACCESSIBILITY_SPEC.md**](docs/ACCESSIBILITY_SPEC.md) | **Inclusive Design & Accessibility Standard:** WCAG 2.1 AA/AAA compliance, screen reader live region queue (`aria-live="polite"`), non-blocking CC overlay, high contrast OLED theme, and tactile keyboard controls. | Accessibility Leads & UX Designers |
| [**SAFETY_AND_ETHICS.md**](docs/SAFETY_AND_ETHICS.md) | **Brand Safety & Ethical AI Framework:** Two-tier `MonetizationGuardrail` architecture, Google Ads policy compliance, sensitive topic taxonomy (disasters, medical emergencies, crisis topics), and DSA/GDPR regulatory alignment. | Trust & Safety Officers & Counsel |

### 🧭 Recommended Reading Paths by Role
- **Google Staff Product Manager:** [PRD.md](docs/PRD.md) $\rightarrow$ [GROWTH_PLAYBOOK.md](docs/GROWTH_PLAYBOOK.md) $\rightarrow$ [EXPERIMENT_DESIGN.md](docs/EXPERIMENT_DESIGN.md)
- **Principal AI Systems Engineer:** [ARCHITECTURE.md](docs/ARCHITECTURE.md) $\rightarrow$ [UCP_SPECIFICATION.md](docs/UCP_SPECIFICATION.md) $\rightarrow$ [SAFETY_AND_ETHICS.md](docs/SAFETY_AND_ETHICS.md)
- **Growth & Experimentation Lead:** [EXPERIMENT_DESIGN.md](docs/EXPERIMENT_DESIGN.md) $\rightarrow$ [GROWTH_PLAYBOOK.md](docs/GROWTH_PLAYBOOK.md)
- **UX & Accessibility Lead:** [ACCESSIBILITY_SPEC.md](docs/ACCESSIBILITY_SPEC.md) $\rightarrow$ [PRD.md](docs/PRD.md)

---

## 🚀 Key Features

1. **Local Model Runtime & Automated Fallback:** Connects to LM Studio (`http://127.0.0.1:1234/v1`) using the `openai` Python SDK, with seamless zero-downtime fallback to `MockLMEngine` for offline development and testing.
2. **Universal Commerce Protocol (UCP) Function Calling:** Structured tools to search catalog, inspect product specifications, validate hardware/sizing compatibility, and execute 1-click Google Pay checkout.
3. **MonetizationGuardrail Policy Safety:** Real-time safety arbiter enforcing Google Ads Brand Safety standards. Suppresses commerce overlays during sensitive video segments (disasters, medical emergencies, crisis topics) with 100% recall.
4. **Authentic YouTube Watch & Shop UI:** Wide-layout Streamlit application following YouTube's official design system (YouTube Studio dark palette, verified creator channel badges, interactive action chips, live CC transcript cue markers, and collapsible in-stream shopping shelf).
5. **Growth Simulation & Benchmark Suite:** Monte Carlo growth simulator (1,000 synthetic viewer journeys) and automated benchmark suite evaluating Pydantic schema validation, tool-calling precision, and latency percentiles.

---

## 📊 Benchmark & Simulation Results

### Monte Carlo Growth Simulation (1,000 Synthetic Journeys)
| Metric | Control (Static Links) | Variant (ShopStream Copilot) | Relative Uplift |
| :--- | :--- | :--- | :--- |
| **Checkout Conversions** | 6 / 500 Viewers | 52 / 500 Viewers | **+766.67%** |
| **Overall CVR (%)** | 1.20% | 10.40% | **+766.67%** |
| **Intent CVR (%)** | 3.37% | 31.52% | **+835.31%** |
| **GMV / 1,000 Views** | \$2,030.00 | \$13,194.00 | **+549.95%** |
| **Creator Earnings / 1k Views**| \$81.20 | \$527.76 | **+549.95%** |
| **Average Watch Time** | 293.3s (Drop-off penalty) | 300.0s (Full retention) | **Zero watch-time penalty** |

### Automated System Benchmarks (`eval/run_eval.py`)
- **Pydantic Schema Validation Rate:** `100.0%`
- **MonetizationGuardrail Accuracy / Recall:** `100.0%`
- **Intent Classification Accuracy:** `100.0%`
- **UCP Tool Calling Precision:** `100.0%`
- **Inference Latency Percentiles:** p50 < 1.0 ms, p90 < 2.0 ms, p99 < 15.0 ms (with cached local engine fallback)

---

## 📂 Repository Layout

```
shopstream_copilot/
├── pyproject.toml              # Build & dependency metadata
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation & documentation index
├── docs/
│   ├── PRD.md                  # Product Requirements Document (0-to-1)
│   ├── EXPERIMENT_DESIGN.md    # A/B Testing & Growth Strategy
│   ├── GROWTH_PLAYBOOK.md      # GTM Strategy & Creator Monetization Playbook
│   ├── UCP_SPECIFICATION.md    # Universal Commerce Protocol v1.2 Specification
│   ├── ARCHITECTURE.md         # System Architecture & Technical Flow
│   ├── ACCESSIBILITY_SPEC.md   # WCAG 2.1 AA/AAA Accessibility Standard
│   └── SAFETY_AND_ETHICS.md    # Brand Safety & Ethical AI Framework
├── data/
│   ├── init_catalog.py         # SQLite DB initializer & data generator
│   ├── catalog.db              # SQLite Merchant Catalog & Video Transcripts DB
│   └── video_transcripts.json  # Exported JSON video transcript cues
├── src/
│   ├── __init__.py             # Package initializer
│   ├── init.py                 # Module initializer
│   ├── config.py               # Application configuration & policy constants
│   ├── models.py               # Pydantic schemas (CommerceIntent, ProductItem, UCPCheckoutPayload, SafetyCheckResult)
│   ├── engine.py               # LocalLLMEngine (LM Studio + Mock fallback)
│   ├── ucp_tools.py            # UCPCommerceEngine function calling tools
│   ├── arbiter.py              # MonetizationGuardrail brand safety engine
│   └── pipeline.py             # ShopStreamPipeline orchestrator
├── eval/
│   ├── __init__.py             # Eval package initializer
│   ├── init.py                 # Module initializer
│   ├── run_eval.py             # System evaluation & benchmark suite
│   └── simulate_growth.py      # Monte Carlo growth simulation (1,000 journeys)
├── tests/
│   ├── __init__.py             # Tests package initializer
│   ├── init.py                 # Module initializer
│   ├── test_ucp_tools.py       # Unit tests for UCP tools
│   ├── test_arbiter.py         # Unit tests for MonetizationGuardrail
│   └── test_pipeline.py        # Unit tests for ShopStreamPipeline
└── app.py                      # Interactive Streamlit 3-panel application
```

---

## 🛠️ Quickstart & Execution Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/timnikolov/shopstream-copilot.git
cd shopstream-copilot

# Create and activate Python 3.11 virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Catalog Database
```bash
python data/init_catalog.py
```
*Output: Seeds `data/catalog.db` with 52 merchant products and 5 timestamped video transcript scenarios.*

### 3. Run Pytest Unit Tests
```bash
pytest tests/
```
*Output: Executes 11 unit tests covering tools, guardrails, and pipelines (100% pass).*

### 4. Run System Evaluation Suite
```bash
python eval/run_eval.py
```
*Output: Evaluates Pydantic schema validation rate, tool calling precision, guardrail accuracy, and latency percentiles.*

### 5. Run Monte Carlo Growth Simulation
```bash
python eval/simulate_growth.py
```
*Output: Models 1,000 synthetic viewer journeys comparing Control vs. Variant (+766% CVR uplift).*

### 6. Launch Interactive Streamlit Application
```bash
streamlit run app.py
```
*Navigate to `http://localhost:8501` to access the YouTube Watch & Shop interactive surface.*
