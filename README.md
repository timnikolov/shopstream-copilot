# ShopStream-Copilot
### In-Stream Video Commerce & Universal Commerce Protocol Agent
**YouTube Shopping Consumer Growth Team — Zurich**

---

## Overview

ShopStream-Copilot is an in-stream commerce platform for YouTube that allows viewers to discover, evaluate, and purchase creator-featured products directly within the video player without interrupting playback.

Today, creator commerce relies on static links pasted into video descriptions. This creates severe drop-off: viewers must leave the video, open external retailer sites, and manually enter shipping and payment details. The result is low conversion rates (under 1.5%) and lost watch time.

ShopStream-Copilot replaces description links with an interactive, in-stream shopping drawer powered by the **Universal Commerce Protocol (UCP)**. It indexes timestamped video transcripts, parses viewer intent in real time, validates hardware and sizing compatibility against local catalog data, and enables 1-click Google Pay checkout.

```
YouTube Watch Surface ──> Context Engine ──> MonetizationGuardrail ──> UCP Engine ──> 1-Click Google Pay
 (Video + Transcript)     (Intent Parser)    (Brand Safety Check)     (Catalog/Specs)  (Tokenized Settlement)
```

---

## Business & Growth Impact

Our Monte Carlo simulation ($N = 1,000$ synthetic viewer journeys, 50/50 split) demonstrates significant gains across both commerce and engagement metrics:

| Metric | Control (Description Links) | Variant (ShopStream Copilot) | Delta |
| :--- | :--- | :--- | :--- |
| **Checkout Conversion Rate (CVR)** | 1.20% | 10.40% | **+766.7%** |
| **Commercial Intent CVR** | 3.37% | 31.52% | **+835.3%** |
| **GMV / 1,000 Views** | \$2,030.00 | \$13,194.00 | **+549.9%** |
| **Creator Earnings / 1,000 Views** | \$81.20 | \$527.76 | **+549.9%** |
| **Average Watch-Time Penalty** | -6.7s per viewer | 0.0s (in-stream playback continues) | **100% retention** |

---

## Core Capabilities

1. **In-Stream Discovery & Compatibility:** Viewers can ask conversational questions (e.g., *"Does this lens fit an E-mount body?"* or *"Is this coat true to size?"*) and receive immediate, spec-verified answers.
2. **Universal Commerce Protocol (UCP v1.2):** Standardized, tokenized transaction protocol that coordinates SKU availability, creator affiliate splits, and 1-click Google Pay execution in sub-10ms latency.
3. **MonetizationGuardrail (Brand Safety):** Real-time safety engine enforcing Google Ads policies. If a video segment touches sensitive topics (crisis, emergency, tragedy), commercial overlays are automatically suppressed with 100% recall.
4. **Local Model Runtime with Fallback:** Connects to local LM Studio instances (`http://127.0.0.1:1234/v1`) using the OpenAI API, with automatic fallback to a deterministic rule-based engine when offline.

---

## Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.11)

### 1. Setup Environment
```bash
git clone https://github.com/timnikolov/shopstream-copilot.git
cd shopstream-copilot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Catalog Database
```bash
python data/init_catalog.py
```
*Seeds `data/catalog.db` with 52 merchant SKUs across tech, fashion, gaming, and beauty, plus 5 video transcript scenarios.*

### 3. Run the Interactive Surface
```bash
streamlit run app.py
```
*Access the YouTube Watch & Shop UI at `http://localhost:8501`.*

### 4. Run Tests & Evaluation
```bash
pytest tests/
python eval/run_eval.py
python eval/simulate_growth.py
```

---

## Documentation Index

For detailed product, growth, and technical specifications, refer to the documentation suite in `docs/`:

- [**PRD.md**](docs/PRD.md): 0-to-1 Product Requirements Document covering user stories, marketplace value, and rollout milestones.
- [**GROWTH_PLAYBOOK.md**](docs/GROWTH_PLAYBOOK.md): Creator acquisition flywheel, GTM rollout phases (DACH $\rightarrow$ EMEA $\rightarrow$ Global), and North Star metric trees.
- [**EXPERIMENT_DESIGN.md**](docs/EXPERIMENT_DESIGN.md): A/B testing strategy, MDE power calculations, guardrail metrics, and sequential testing rules.
- [**UCP_SPECIFICATION.md**](docs/UCP_SPECIFICATION.md): Universal Commerce Protocol v1.2 technical messaging flow, JSON schemas, error codes, and settlement security.
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): System architecture, pipeline lifecycle, and LM Studio integration.
- [**ACCESSIBILITY_SPEC.md**](docs/ACCESSIBILITY_SPEC.md): WCAG 2.1 AA/AAA compliance, screen reader live regions (`aria-live`), and non-blocking closed caption layout.
- [**SAFETY_AND_ETHICS.md**](docs/SAFETY_AND_ETHICS.md): Google AI principles alignment, sensitive topic taxonomy, and regulatory compliance (DSA, GDPR, FADP).

---

## Repository Structure

```
shopstream_copilot/
├── app.py                  # YouTube Watch & Shop Streamlit surface
├── pyproject.toml          # Project configuration & test paths
├── requirements.txt        # Runtime dependencies
├── data/                   # SQLite catalog (52 SKUs) & video transcripts
├── docs/                   # Product, growth, and technical documentation
├── src/                    # Core pipeline, UCP tools, guardrails, and models
├── eval/                   # Benchmarks & Monte Carlo growth simulator
└── tests/                  # Pytest unit tests (tools, arbiter, pipeline)
```
