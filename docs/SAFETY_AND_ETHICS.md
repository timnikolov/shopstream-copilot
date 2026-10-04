# Brand Safety, Policy & Ethical AI Framework
## MonetizationGuardrail & Regulatory Compliance Specification
**Organization:** Trust & Safety and Responsible AI Governance  
**Document ID:** SAF-2026-SSC-002  
**Target Policies:** Sensitive Content Brand Safety Guidelines & Community Standards  

---

## 1. Ethical Mission & Core Principles

Commercial monetization must **never compromise human dignity or exploit human tragedy**. Video commerce must remain strictly compliant with Google’s Brand Safety standards. 

When video content touches on sensitive topics such as natural disasters, armed conflict, mass casualties, medical emergencies, or personal bereavement, all commercial features, product overlays, and purchasing call-to-actions must be **immediately suppressed**.

---

## 2. Alignment with Google AI Principles

| Google AI Principle | ShopStream-Copilot Implementation |
| :--- | :--- |
| **1. Be socially beneficial** | Enhances viewer convenience while deterministically respecting creator attribution and merchant inventory fidelity. |
| **2. Avoid creating or reinforcing unfair bias** | Catalog recommendations and compatibility validations evaluate objective hardware and technical specifications without profiling sensitive personal demographics. |
| **3. Be built and tested for safety** | Two-tier safety guardrail: database metadata cues combined with real-time NLP spoken transcript regex verification. |
| **4. Be accountable to people** | Fallback to human review and creator appeals when automated monetization guardrails suppress commerce features. |
| **5. Incorporate privacy by design** | Tokenized Google Pay transactions; zero raw credit card or address data stored by the agent runtime. |

---

## 3. Sensitive Category Taxonomy & Guardrail Logic

`MonetizationGuardrail` evaluates each video cue against seven non-monetizable categories:

```
                          ┌──────────────────────────────────────┐
                          │   Current Playback Timestamp (t)     │
                          └──────────────────┬───────────────────┘
                                             │
                                             ▼
                          ┌──────────────────────────────────────┐
                          │   Tier 1: Video Cue Metadata Lookup   │
                          │      (catalog.db transcript tags)    │
                          └──────────────────┬───────────────────┘
                                             │
                                             ▼
                          ┌──────────────────────────────────────┐
                          │  Tier 2: Real-Time Spoken Text NLP   │
                          │   (Regex & Semantic Keyword Scan)    │
                          └──────────────────┬───────────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [ Sensitive Detected ]                      [ Segment Compliant ]
                       │                                           │
                       ▼                                           ▼
          Risk Score $\ge$ 0.70                      Risk Score = 0.02
          is_safe_to_monetize = False                is_safe_to_monetize = True
          • Suppress shopping overlays               • Enable UCP tools
          • Informative viewer banner                • Active 1-Click checkout
```

### Sensitive Categories Table
1. **Natural & Humanitarian Disasters:** Earthquakes, tsunamis, floods, evacuations, extreme wildfires.
2. **Violence & Tragedy:** Shootings, terrorist attacks, fatal accidents, riots.
3. **Medical Emergencies & Health Crises:** Pandemic escalations, hospital trauma care, severe casualties.
4. **Self-Harm & Mental Health Crises:** Suicide references, eating disorders, self-harm discussions.
5. **Bereavement & Grief:** Funerals, eulogies, tragic loss memoirs.
6. **War & Military Conflicts:** Active warfare reports, bomb strikes, military hostage situations.
7. **Hate Speech & Political Extremism:** Defamatory speech, election interference, harassment.

---

## 4. Regulatory & Privacy Compliance

- **Swiss FADP & EU GDPR:** Zero persistent viewer tracking across third-party websites. Viewer IDs are ephemeral session hashes.
- **EU Digital Services Act (DSA):** Full transparency in automated recommendation logic. When an item is recommended because it is featured by a creator, the UI clearly discloses creator affiliate remuneration.
- **PCI-DSS Level 1 Compliance:** The host agent never interacts with primary account numbers (PAN). Google Pay handles tokenization and card issuer cryptograms directly on secure client hardware.
