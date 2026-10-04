import sys
import random
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

def run_monte_carlo_growth_simulation(n_users: int = 1000, seed: int = 42):
    """Run Monte Carlo simulation comparing Control (Description Links) vs Variant (ShopStream-Copilot).
    
    Args:
        n_users: Total synthetic viewers to simulate (split 50/50).
        seed: Random seed for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)

    half_n = n_users // 2

    # Product price distributions for synthetic purchases ($20 to $500)
    def sample_order_value():
        return float(np.random.choice([25.0, 48.0, 98.0, 170.0, 299.0, 649.0, 2298.0], p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.04, 0.01]))

    # Commission rate (average 8%)
    commission_rate = 0.08

    # Simulated metrics accumulators
    control_metrics = {
        "group": "Control (Description Links)",
        "viewers": half_n,
        "commercial_intents": 0,
        "drawer_opens": 0,
        "checkouts": 0,
        "total_gmv": 0.0,
        "creator_earnings": 0.0,
        "watch_time_lost_sec": 0.0,
        "abandonments": 0
    }

    variant_metrics = {
        "group": "Variant (ShopStream-Copilot)",
        "viewers": half_n,
        "commercial_intents": 0,
        "drawer_opens": 0,
        "checkouts": 0,
        "total_gmv": 0.0,
        "creator_earnings": 0.0,
        "watch_time_lost_sec": 0.0,
        "abandonments": 0
    }

    # Base video duration in seconds
    base_video_duration = 300.0

    # 1. Simulate Control Group (Description Links)
    for _ in range(half_n):
        has_commercial_intent = random.random() < 0.35
        if has_commercial_intent:
            control_metrics["commercial_intents"] += 1
            # User must scroll to video description and click external affiliate link
            clicks_description = random.random() < 0.28
            if clicks_description:
                control_metrics["drawer_opens"] += 1
                # External site navigation causes watch-time drop-off
                watch_time_loss = random.uniform(30.0, 90.0)
                control_metrics["watch_time_lost_sec"] += watch_time_loss
                
                # External checkout conversion rate (high friction, re-entering payment info)
                converts = random.random() < 0.16
                if converts:
                    control_metrics["checkouts"] += 1
                    order_val = sample_order_value()
                    control_metrics["total_gmv"] += order_val
                    control_metrics["creator_earnings"] += (order_val * commission_rate)
                else:
                    control_metrics["abandonments"] += 1
            else:
                control_metrics["abandonments"] += 1

    # 2. Simulate Variant Group (ShopStream-Copilot Agent)
    for _ in range(half_n):
        has_commercial_intent = random.random() < 0.35
        if has_commercial_intent:
            variant_metrics["commercial_intents"] += 1
            # In-stream automated assistant opens interactive drawer without pausing video
            engages_copilot = random.random() < 0.72
            if engages_copilot:
                variant_metrics["drawer_opens"] += 1
                # Zero watch-time loss penalty (in-stream playback continues)
                
                # Instant UCP 1-Click Google Pay Checkout with compatibility auto-check
                converts = random.random() < 0.45
                if converts:
                    variant_metrics["checkouts"] += 1
                    order_val = sample_order_value()
                    variant_metrics["total_gmv"] += order_val
                    variant_metrics["creator_earnings"] += (order_val * commission_rate)
                else:
                    variant_metrics["abandonments"] += 1
            else:
                variant_metrics["abandonments"] += 1

    # Calculate derived KPIs
    def compute_kpis(m):
        cvr_overall = (m["checkouts"] / m["viewers"]) * 100.0
        cvr_intent = (m["checkouts"] / m["commercial_intents"] * 100.0) if m["commercial_intents"] > 0 else 0.0
        gmv_per_kv = (m["total_gmv"] / m["viewers"]) * 1000.0
        avg_watch_time = base_video_duration - (m["watch_time_lost_sec"] / m["viewers"])
        return {
            "Group": m["group"],
            "Total Viewers": m["viewers"],
            "Commercial Intent Rate": f"{(m['commercial_intents']/m['viewers'])*100:.1f}%",
            "Checkout Conversions": m["checkouts"],
            "Overall CVR (%)": f"{cvr_overall:.2f}%",
            "Intent CVR (%)": f"{cvr_intent:.2f}%",
            "Total GMV ($)": f"${m['total_gmv']:,.2f}",
            "GMV / 1,000 Views ($)": f"${gmv_per_kv:,.2f}",
            "Creator Earnings ($)": f"${m['creator_earnings']:,.2f}",
            "Avg Watch Time (s)": f"{avg_watch_time:.1f}s",
            "Funnel Abandonment Rate": f"{(m['abandonments']/m['commercial_intents'])*100:.1f}%"
        }

    c_kpi = compute_kpis(control_metrics)
    v_kpi = compute_kpis(variant_metrics)

    df_results = pd.DataFrame([c_kpi, v_kpi])

    # Calculate Relative Uplift
    cvr_c = (control_metrics["checkouts"] / control_metrics["viewers"])
    cvr_v = (variant_metrics["checkouts"] / variant_metrics["viewers"])
    cvr_uplift = ((cvr_v - cvr_c) / cvr_c) * 100.0 if cvr_c > 0 else 0.0

    gmv_c = (control_metrics["total_gmv"] / control_metrics["viewers"]) * 1000.0
    gmv_v = (variant_metrics["total_gmv"] / variant_metrics["viewers"]) * 1000.0
    gmv_uplift = ((gmv_v - gmv_c) / gmv_c) * 100.0 if gmv_c > 0 else 0.0

    print("================================================================================")
    print("      YOUTUBE SHOPPING ZURICH - MONTE CARLO GROWTH SIMULATION RESULTS           ")
    print("================================================================================")
    print(f"Sample Size: {n_users} Synthetic Viewer Journeys (500 Control / 500 Variant)\n")
    print(df_results.to_string(index=False))
    print("\n--------------------------------------------------------------------------------")
    print(f"🚀 OVERALL CVR UPLIFT:      +{cvr_uplift:.2f}% (Control {cvr_c*100:.2f}% -> Variant {cvr_v*100:.2f}%)")
    print(f"💰 GMV / 1k VIEWS UPLIFT:   +{gmv_uplift:.2f}% (${gmv_c:.2f} -> ${gmv_v:.2f})")
    print(f"⏱️ WATCH TIME RETENTION:   Zero playback drop-off penalty with ShopStream Copilot")
    print("================================================================================")

    return df_results

if __name__ == "__main__":
    run_monte_carlo_growth_simulation()
