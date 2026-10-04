# Experimentation & A/B Testing Specification
## ShopStream-Copilot vs. Control (Static Description Links)
**Team:** YouTube Shopping Consumer Growth Team (Zurich)  
**Document ID:** EXP-2026-YTS-009  

---

## 1. Primary Hypotheses

### Hypothesis H1 (Conversion Rate Uplift)
Deploying the ShopStream-Copilot in-stream AI agent with UCP 1-Click Google Pay checkout will increase overall viewer checkout conversion rate (CVR) by **>= +300% relative** compared to the legacy description links control arm.

### Hypothesis H2 (Watch-Time Retention)
Allowing viewers to query product compatibility and purchase in-stream without leaving playback will eliminate the watch-time drop-off penalty, resulting in a **>= 5.0% increase in average watch-time per session**.

---

## 2. Metric Framework

### 2.1 Primary Metrics
- **Overall Conversion Rate (CVR %):** `Total Completed Purchases / Total Video Viewers`
- **Gross Merchandise Value per Thousand Views (GMV / kV):** `(Total Completed GMV / Total Views) * 1000`

### 2.2 Secondary Metrics
- **In-Stream Drawer Engagement Rate (%):** `Viewers Interacting with ShopStream Drawer / Total Viewers`
- **Creator Earnings per Thousand Views ($):** `(Total Creator Commission / Total Views) * 1000`
- **Intent Resolution Precision (%):** Accuracy of parsed intent against viewer queries.

### 2.3 Guardrail Metrics (Must Not Degrade)
- **Average Watch Time Retention (Seconds):** Target delta >= 0.0s (No statistically significant decrease).
- **Unsubscribe Rate (%):** Channel unsubscribe events per 10,000 views must not increase by > 0.01%.
- **Ad Block / Opt-out Rate (%):** User requests to disable in-stream shopping drawer must remain < 0.5%.

---

## 3. Minimum Detectable Effect (MDE) & Power Calculations

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **Control Baseline CVR ($p_1$)** | 1.50% | Legacy YouTube description link conversion rate |
| **Expected Variant CVR ($p_2$)** | 6.00% | Target 4x relative uplift from in-stream UCP 1-click |
| **Significance Level ($\alpha$)** | 0.05 | Two-tailed standard significance threshold |
| **Statistical Power ($1 - \beta$)** | 0.80 | Standard 80% power target |
| **Required Sample Size per Arm ($N$)** | ~1,250 Viewers | Calculated via Two-Proportions Z-Test Formula |

$$\text{MDE} = Z_{1-\alpha/2} \sqrt{2 \bar{p}(1-\bar{p}) / N} + Z_{1-\beta} \sqrt{p_1(1-p_1)/N + p_2(1-p_2)/N}$$

---

## 4. Sample Allocation & Sequential Testing Rules

- **Allocation Split:** 50% Control (Static Description Links) vs. 50% Variant (ShopStream-Copilot).
- **Randomization Unit:** YouTube Viewer ID (`user_id` persistent cookie).
- **Sequential Testing Guard:** mSPRT (mixture Sequential Probability Ratio Test) executed daily to monitor guardrail metrics and allow early stopping if watch time degrades significantly.
