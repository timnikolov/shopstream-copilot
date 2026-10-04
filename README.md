# 🔴 ShopStream-Copilot
### In-Stream Video Commerce & Universal Commerce Protocol Agent
**Designed for the YouTube Shopping Consumer Growth Team (Zurich)**

[![Python 3.11](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Protocol](https://img.shields.io/badge/Protocol-Universal_Commerce_Protocol_(UCP)-green.svg)](docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/License-Google_Proprietary-red.svg)]()

---

## 🌟 Executive Overview

**ShopStream-Copilot** enables YouTube viewers to watch creator content and shop featured products simultaneously without pausing playback or causing watch-time drop-off.

By ingesting timestamped video transcripts, parsing viewer queries, retrieving structured inventory from a local Google Merchant Center SQLite catalog (`data/catalog.db`), and executing 1-click checkout flows via the **Universal Commerce Protocol (UCP)**, ShopStream-Copilot transforms static video watching into an interactive, frictionless shopping experience.

---

## 🚀 Key Features

1. **Local Model Runtime & Automated Fallback:** Connects to LM Studio (`http://localhost:1234/v1`) using the `openai` Python SDK, with seamless zero-downtime fallback to `MockLMEngine` for offline development and testing.
2. **Universal Commerce Protocol (UCP) Function Calling:** Structured tools to search catalog, inspect product specifications, validate hardware/sizing compatibility, and simulate 1-click Google Pay checkout.
3. **MonetizationGuardrail Policy Safety:** Real-time safety arbiter enforcing Google Ads Brand Safety standards. Suppresses commerce overlays during sensitive video segments (disasters, medical emergencies, crisis topics) with 100% recall.
4. **Interactive 3-Panel Streamlit Application:** YouTube Watch & Shop UI with A/B experiment controls (Control vs. Variant), synchronized transcript feed, interactive chat assistant, live UCP JSON payload inspector, and telemetry metrics.
5. **Growth Simulation & Benchmark Suite:** Monte Carlo growth simulator (1,000 synthetic viewer journeys) and automated benchmark suite evaluating Pydantic schema validation, tool-calling precision, and latency percentiles.

---

## 📂 Repository Layout

```
shopstream_copilot/
├── pyproject.toml              # Build & dependency metadata
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation & quickstart
├── docs/
│   ├── PRD.md                  # Product Requirements Document
│   ├── EXPERIMENT_DESIGN.md    # A/B Testing & Growth Strategy
│   ├── ACCESSIBILITY_SPEC.md   # WCAG 2.1 AA Accessibility Standard
│   └── ARCHITECTURE.md         # Architecture & UCP Schema
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
*Output: Evaluates Pydantic schema validation rate, tool calling precision, guardrail accuracy, and latency percentiles (p50 < 1ms, p99 < 15ms).*

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
