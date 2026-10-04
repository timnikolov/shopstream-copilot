import sys
import json
import time
from pathlib import Path
import streamlit as st

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.pipeline import ShopStreamPipeline
from src.arbiter import MonetizationGuardrail
from src.ucp_tools import UCPCommerceEngine
from src.models import PipelineResponse

# Streamlit Page Configuration
st.set_page_config(
    page_title="YouTube Shopping | ShopStream-Copilot",
    page_icon="https://www.youtube.com/s/desktop/f403fa8a/img/favicon_32x32.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "pipeline" not in st.session_state:
    st.session_state.pipeline = ShopStreamPipeline()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "cumulative_gmv" not in st.session_state:
    st.session_state.cumulative_gmv = 0.0

if "cumulative_creator_rev" not in st.session_state:
    st.session_state.cumulative_creator_rev = 0.0

if "checkouts_count" not in st.session_state:
    st.session_state.checkouts_count = 0

if "aria_announcements" not in st.session_state:
    st.session_state.aria_announcements = []

# Video Scenario Metadata Definition
SCENARIOS = {
    "Sony Alpha 7 IV Review (Tech)": {
        "video_id": "vid_sony_alpha",
        "title": "Sony Alpha 7 IV & FE 24-70mm GM II Ultimate Review",
        "channel": "TechVision Pro",
        "subscribers": "1.42M subscribers",
        "avatar_text": "TV",
        "duration": 300,
        "category": "Tech",
        "fallback_mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    },
    "NYC Autumn Fashion Haul (Apparel)": {
        "video_id": "vid_autumn_fashion",
        "title": "NYC Autumn Capsule Wardrobe & Fall Style Haul",
        "channel": "Elena Haute Zurich",
        "subscribers": "840K subscribers",
        "avatar_text": "EH",
        "duration": 300,
        "category": "Apparel",
        "fallback_mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
    },
    "Pacific Rim Earthquake (Crisis / Sensitive)": {
        "video_id": "vid_earthquake_news",
        "title": "BREAKING: 6.8 Earthquake Hits Pacific Rim - Emergency Response Live",
        "channel": "Global News Network",
        "subscribers": "5.1M subscribers",
        "avatar_text": "GN",
        "duration": 300,
        "category": "News",
        "fallback_mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    },
    "Desk Setup 2026 (Gaming)": {
        "video_id": "vid_pro_gaming",
        "title": "Ultimate Desk Setup 2026: OLED Monitors & Custom Keyboards",
        "channel": "BattleStation Zurich",
        "subscribers": "620K subscribers",
        "avatar_text": "BZ",
        "duration": 300,
        "category": "Gaming",
        "fallback_mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoylikes.mp4"
    },
    "Glass Skin K-Beauty (Beauty)": {
        "video_id": "vid_glass_skin",
        "title": "10-Step K-Beauty Glass Skin Evening Routine",
        "channel": "Glow Zurich K-Beauty",
        "subscribers": "1.15M subscribers",
        "avatar_text": "GZ",
        "duration": 300,
        "category": "Beauty",
        "fallback_mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4"
    }
}

# Sidebar - YouTube Studio Controls
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <svg height="28" viewBox="0 0 24 24" width="28" fill="#FF0000">
            <path d="M21.58 7.19c-.23-.86-.91-1.54-1.77-1.77C18.25 5 12 5 12 5s-6.25 0-7.81.42c-.86.23-1.54.91-1.77 1.77C2 8.75 2 12 2 12s0 3.25.42 4.81c.23.86.91 1.54 1.77 1.77C5.75 19 12 19 12 19s6.25 0 7.81-.42c.86-.23 1.54-.91 1.77-1.77C22 15.25 22 12 22 12s0-3.25-.42-4.81zM10 15V9l5.2 3-5.2 3z"/>
        </svg>
        <span style="font-size:1.3rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px;">Studio</span>
    </div>
    <p style="color:#AAAAAA; font-size:0.85rem; margin-top:-8px; margin-bottom:16px;">Consumer Growth Experimentation (Zurich)</p>
    """, unsafe_allow_html=True)

    contrast_theme = st.radio(
        "Theme & Contrast",
        options=["YouTube Dark (Standard AA)", "High Contrast OLED (AAA)"],
        index=0
    )
    is_pure_oled = "OLED" in contrast_theme

    st.markdown("---")
    screen_reader_active = st.toggle("Screen Reader ARIA Live Region", value=True)

    with st.expander("Keyboard Navigation"):
        st.markdown("""
        * **K / Space**: Play/Pause Playback
        * **Shift + S**: Toggle ShopStream Drawer
        * **Shift + C**: 1-Click Google Pay Checkout
        * **M**: Mute Audio
        """)

    st.markdown("---")
    st.markdown("""
    <div style="color:#AAAAAA; font-size:0.8rem; line-height:1.4;">
        <strong>Surface:</strong> YouTube Watch & Shop<br/>
        <strong>Runtime:</strong> LM Studio + Local Fallback<br/>
        <strong>Protocol:</strong> Universal Commerce Protocol (UCP)
    </div>
    """, unsafe_allow_html=True)

# YouTube Design Theme Variables
main_bg = "#000000" if is_pure_oled else "#0F0F0F"
sidebar_bg = "#000000" if is_pure_oled else "#181818"
card_bg = "#121212" if is_pure_oled else "#212121"
card_border = "#FFFF00" if is_pure_oled else "#303030"
primary_text = "#FFFFFF"
secondary_text = "#F1F1F1"
meta_text = "#AAAAAA"
yt_red = "#FF0000"
yt_blue = "#3EA6FF"
yt_green = "#00E676"
yt_amber = "#FFB300"

st.markdown(f"""
<style>
    /* Global YouTube Theme */
    .stApp {{
        background-color: {main_bg} !important;
        color: {primary_text} !important;
        font-family: 'Roboto', 'YouTube Sans', Arial, sans-serif !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid #282828 !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}

    /* Global Typography: eliminate low-contrast text */
    p, span, label, div, li, h1, h2, h3, h4, h5, h6 {{
        color: {primary_text} !important;
    }}

    /* YouTube Pill Buttons */
    .stButton>button {{
        background-color: {yt_red} !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
        font-size: 0.9rem !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }}
    .stButton>button:hover {{
        background-color: #CC0000 !important;
        transform: scale(1.02);
    }}

    /* YouTube Cards */
    .yt-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        border: 1px solid {card_border};
    }}

    /* YouTube Action Chip */
    .yt-chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #272727;
        color: #F1F1F1 !important;
        padding: 6px 14px;
        border-radius: 18px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        border: 1px solid #383838;
    }}
    .yt-chip:hover {{
        background-color: #3F3F3F;
    }}

    /* Badges */
    .badge-live {{
        background-color: #CC0000;
        color: #FFFFFF !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}

    .badge-ucp {{
        background-color: #065FD4;
        color: #FFFFFF !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }}

    /* Active Spoken Transcript Marker */
    .yt-cc-cue {{
        background-color: #272727;
        border-left: 4px solid {yt_red};
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #FFFFFF !important;
    }}

    /* Guardrail Alert */
    .guardrail-alert {{
        background-color: #331A00;
        border: 1px solid {yt_amber};
        border-radius: 8px;
        padding: 14px 18px;
        margin: 12px 0;
        color: #FFE082 !important;
        font-size: 0.9rem;
        line-height: 1.4;
    }}

    /* ARIA Box */
    .aria-box {{
        background-color: #002B11;
        border: 1px solid {yt_green};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #A7F3D0 !important;
    }}

    /* Metrics */
    div[data-testid="stMetricValue"] {{
        color: {yt_green} !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: #E0E0E0 !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP NAVIGATION BAR (Authentic YouTube Header)
# -----------------------------------------------------------------------------
st.markdown("""<div style="display:flex; align-items:center; justify-content:space-between; padding:4px 0 16px 0; border-bottom:1px solid #282828; margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:8px;">
        <svg height="28" viewBox="0 0 24 24" width="28" fill="#FF0000"><path d="M21.58 7.19c-.23-.86-.91-1.54-1.77-1.77C18.25 5 12 5 12 5s-6.25 0-7.81.42c-.86.23-1.54.91-1.77 1.77C2 8.75 2 12 2 12s0 3.25.42 4.81c.23.86.91 1.54 1.77 1.77C5.75 19 12 19 12 19s6.25 0 7.81-.42c.86-.23 1.54-.91 1.77-1.77C22 15.25 22 12 22 12s0-3.25-.42-4.81zM10 15V9l5.2 3-5.2 3z"/></svg>
        <span style="font-size:1.45rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px;">YouTube</span>
        <span style="background-color:#272727; color:#E0E0E0; font-size:0.75rem; font-weight:700; padding:2px 6px; border-radius:4px; margin-left:4px;">Shopping</span>
    </div>
    <div style="display:flex; align-items:center; width:45%; max-width:600px;">
        <div style="display:flex; width:100%; background:#121212; border:1px solid #333333; border-radius:40px; padding:6px 16px;">
            <span style="color:#AAAAAA; font-size:0.9rem;">Search featured video gear, apparel, beauty...</span>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:10px;">
        <span class="badge-live">LIVE</span>
        <span class="badge-ucp">UCP v1.2</span>
        <div style="width:32px; height:32px; border-radius:50%; background:#065FD4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.85rem; color:#FFFFFF;">Z</div>
    </div>
</div>""", unsafe_allow_html=True)

# Layout Setup: 3 Columns
col_controls, col_player, col_telemetry = st.columns([1.1, 2.3, 1.2], gap="large")

# -----------------------------------------------------------------------------
# COLUMN 1: Experiment & Scenario Controls
# -----------------------------------------------------------------------------
with col_controls:
    st.markdown("<h3 style='margin:0 0 10px 0; font-size:1.15rem; font-weight:800;'>Experiment Surface</h3>", unsafe_allow_html=True)
    
    experiment_arm = st.radio(
        "A/B Allocation Arm",
        options=["Variant (ShopStream In-Stream)", "Control (Description Links)"],
        index=0,
        help="Variant enables interactive in-stream commerce drawer with 1-click UCP checkout."
    )
    is_variant = "Variant" in experiment_arm

    st.markdown("---")
    st.markdown("<h3 style='margin:0 0 10px 0; font-size:1.15rem; font-weight:800;'>Video Scenario</h3>", unsafe_allow_html=True)
    selected_scenario = st.selectbox(
        "Select Video Stream",
        options=list(SCENARIOS.keys()),
        index=0
    )
    scenario = SCENARIOS[selected_scenario]
    video_id = scenario["video_id"]

    st.markdown("---")
    st.markdown("<h3 style='margin:0 0 10px 0; font-size:1.15rem; font-weight:800;'>Screen Reader ARIA</h3>", unsafe_allow_html=True)
    if screen_reader_active:
        if st.session_state.aria_announcements:
            latest = st.session_state.aria_announcements[-1]
            st.markdown(f"""
            <div class="aria-box" role="status" aria-live="polite">
                🗣️ <strong>[aria-live="polite"]:</strong><br/>
                "{latest}"
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#AAAAAA; font-size:0.85rem;'>Monitoring stream for live announcements...</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#AAAAAA; font-size:0.85rem;'>Screen reader announcements disabled.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div class="yt-card">
        <h4 style="margin:0 0 6px 0; font-size:0.95rem; font-weight:700;">Cohort Specs</h4>
        <div style="font-size:0.82rem; color:#E0E0E0; line-height:1.5;">
            • Region: Zurich, CH<br/>
            • Surface: Watch Player<br/>
            • Merchant Catalog: 52 SKUs
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# COLUMN 2: YouTube Watch Player, Channel Row & ShopStream Drawer
# -----------------------------------------------------------------------------
with col_player:
    # 1. LIVE VIDEO PLAYER
    st.video(scenario["fallback_mp4"])

    # 2. VIDEO TITLE & CHANNEL METADATA ROW
    st.markdown(f"""
    <div style="margin-top:12px; margin-bottom:12px;">
        <h2 style="margin:0; font-size:1.35rem; font-weight:800; color:#FFFFFF; line-height:1.3;">{scenario['title']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Channel Info, Subscribe Button, and YouTube Action Pills
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:40px; height:40px; border-radius:50%; background:#272727; border:1px solid #444; display:flex; align-items:center; justify-content:center; font-weight:800; color:#FFFFFF;">
                {scenario['avatar_text']}
            </div>
            <div>
                <div style="font-weight:700; color:#FFFFFF; font-size:0.95rem; display:flex; align-items:center; gap:4px;">
                    {scenario['channel']}
                    <svg height="14" viewBox="0 0 24 24" width="14" fill="#AAAAAA"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zM9.8 17.3l-4.2-4.1 1.4-1.4 2.8 2.7 7.8-7.9 1.4 1.4-9.2 9.3z"/></svg>
                </div>
                <div style="font-size:0.8rem; color:#AAAAAA;">{scenario['subscribers']}</div>
            </div>
            <button style="background:#FFFFFF; color:#0F0F0F; border:none; border-radius:18px; padding:6px 16px; font-weight:700; font-size:0.85rem; cursor:pointer; margin-left:8px;">
                Subscribe
            </button>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
            <div class="yt-chip">👍 18K</div>
            <div class="yt-chip">Share</div>
            <div class="yt-chip">Download</div>
            <div class="yt-chip">Save</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#282828; margin:16px 0;'/>", unsafe_allow_html=True)

    # 3. TIMELINE SCRUBBER & TRANSCRIPT SYNCHRONIZER
    st.markdown("<h4 style='margin:0 0 6px 0; font-size:0.95rem; font-weight:700;'>Playback Scrubber & Synchronized Transcript</h4>", unsafe_allow_html=True)
    playback_time = st.slider(
        "Timestamp (Seconds)",
        min_value=0.0,
        max_value=float(scenario["duration"]),
        value=20.0,
        step=5.0,
        label_visibility="collapsed"
    )

    # Lookup Active Cue & Guardrail Status
    guardrail: MonetizationGuardrail = st.session_state.pipeline.guardrail
    active_cue = guardrail.get_active_transcript_cue(video_id, playback_time)
    safety_result = guardrail.check_monetization_safety(video_id, playback_time)

    # Add Screen Reader Announcement
    if active_cue and screen_reader_active:
        announcement = f"Spoken at {active_cue['timestamp_start']:.0f}s: {active_cue['text']}"
        if not st.session_state.aria_announcements or st.session_state.aria_announcements[-1] != announcement:
            st.session_state.aria_announcements.append(announcement)

    # Display Active Transcript Box
    if active_cue:
        st.markdown(f"""
        <div class="yt-cc-cue">
            <span style="color:#FF0000; font-weight:800;">[{active_cue['timestamp_start']:.0f}s - {active_cue['timestamp_end']:.0f}s]</span>
            <strong style="color:#FFFFFF; margin-left:4px;">{active_cue['speaker']}:</strong>
            <span style="color:#F1F1F1; margin-left:6px;">"{active_cue['text']}"</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#AAAAAA; font-size:0.85rem;'>[No spoken transcript cue at current timestamp]</p>", unsafe_allow_html=True)

    # Brand Safety Policy Alert
    if not safety_result.is_safe_to_monetize:
        st.markdown(f"""
        <div class="guardrail-alert" role="alert">
            <strong>MonetizationGuardrail Policy Active:</strong> Commercial features suppressed.<br/>
            <span style="color:#FFF;">{safety_result.reason}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#282828; margin:16px 0;'/>", unsafe_allow_html=True)

    # 4. IN-STREAM COMMERCE SURFACE (VARIANT VS CONTROL)
    if is_variant:
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.1rem;">🛍️</span>
                <span style="font-weight:800; font-size:1.05rem; color:#FFFFFF;">Products in this video</span>
            </div>
            <span style="color:#AAAAAA; font-size:0.8rem; font-weight:600;">Universal Commerce Protocol</span>
        </div>
        """, unsafe_allow_html=True)

        if not safety_result.is_safe_to_monetize:
            st.warning("Shopping overlay is currently hidden due to Brand Safety policy compliance.")
        else:
            ucp_engine: UCPCommerceEngine = st.session_state.pipeline.ucp_engine
            featured_skus = active_cue.get("featured_skus", []) if active_cue else []
            display_products = []
            for s in featured_skus:
                p = ucp_engine.get_product_details(s)
                if p:
                    display_products.append(p)

            if not display_products:
                display_products = ucp_engine.search_catalog(query="", category=scenario["category"], max_results=2)

            t_products, t_compat, t_split = st.tabs(["Featured Products", "Specs & Compatibility", "Creator Split"])

            with t_products:
                for prod in display_products:
                    st.markdown(f"""
                    <div class="yt-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; color:#FFFFFF; font-size:1.05rem;">{prod.title}</div>
                                <div style="color:#AAAAAA; font-size:0.85rem; margin-top:2px;">{prod.brand} • In Stock</div>
                                <div style="color:#00E676; font-size:1.15rem; font-weight:800; margin-top:4px;">${prod.price:.2f} {prod.currency}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns([2, 1])
                    with btn_c1:
                        st.caption(f"Specs: {json.dumps(prod.specs)}")
                    with btn_c2:
                        if st.button("⚡ 1-Click Buy", key=f"btn_buy_{prod.sku_id}"):
                            res: PipelineResponse = st.session_state.pipeline.process_viewer_request(
                                video_id=video_id,
                                timestamp_sec=playback_time,
                                user_query=f"Buy {prod.sku_id} with 1-click",
                                user_id="usr_yt_zurich_882"
                            )
                            st.session_state.last_response = res
                            if res.checkout_payload:
                                st.session_state.cumulative_gmv += res.checkout_payload.total_amount
                                st.session_state.cumulative_creator_rev += res.checkout_payload.creator_commission_amount
                                st.session_state.checkouts_count += 1
                                if screen_reader_active:
                                    st.session_state.aria_announcements.append(
                                        f"ORDER CONFIRMED: {prod.title} for ${res.checkout_payload.total_amount:.2f} USD."
                                    )
                            st.success(f"Order Confirmed via Google Pay! Transaction: `{res.checkout_payload.transaction_id if res.checkout_payload else 'N/A'}`")

            with t_compat:
                st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#FFF;'>Hardware & Size Validation</h4>", unsafe_allow_html=True)
                target = display_products[0] if display_products else None
                if target:
                    user_ctx = {"camera_mount": "Sony E-mount", "shoe_size": "US 10", "skin_type": "sensitive"}
                    compat_res = ucp_engine.validate_compatibility(target.sku_id, user_ctx)
                    if compat_res["compatible"]:
                        st.success(f"✅ Compatible: {compat_res['reasons'][0]}")
                    else:
                        st.error(f"❌ Incompatible: {compat_res['reasons'][0]}")
                    st.json(compat_res["specs_checked"])

            with t_split:
                st.markdown(f"""
                <div class="yt-card">
                    <div style="font-size:0.9rem; color:#FFFFFF; line-height:1.6;">
                        • <strong>Channel:</strong> {scenario['channel']}<br/>
                        • <strong>Affiliate Split:</strong> 8.5% instant attribution<br/>
                        • <strong>Settlement Rail:</strong> Google Pay / UCP Tokenized
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        # CONTROL ARM: Static YouTube Description Box
        st.markdown("""
        <div class="yt-card">
            <h4 style="margin:0 0 6px 0; color:#FFFFFF; font-size:0.95rem;">Video Description (External Links)</h4>
            <div style="font-size:0.85rem; color:#AAAAAA; margin-bottom:8px;">Featured equipment and items mentioned in this video:</div>
            <ul style="font-size:0.88rem; margin:0 0 8px 16px; padding:0;">
                <li><a href="#" style="color:#3EA6FF;">Sony Alpha 7 IV - Retailer Link (Opens external tab)</a></li>
                <li><a href="#" style="color:#3EA6FF;">Sony FE 24-70mm GM II - Retailer Link (Opens external tab)</a></li>
                <li><a href="#" style="color:#3EA6FF;">Rode VideoMic Pro+ - Retailer Link (Opens external tab)</a></li>
            </ul>
            <div style="font-size:0.78rem; color:#FFE082;">⚠️ Clicking description links navigates away from playback and creates watch-time drop-off.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#282828; margin:16px 0;'/>", unsafe_allow_html=True)

    # 5. LIVE VIEWER CHAT ASSISTANT
    st.markdown("<h4 style='margin:0 0 8px 0; font-size:1.0rem; font-weight:800; color:#FFF;'>ShopStream Viewer Assistant</h4>", unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        st.chat_message(chat["role"]).write(chat["content"])

    user_query = st.chat_input("Ask about featured gear, sizing, or 1-click buy...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        response: PipelineResponse = st.session_state.pipeline.process_viewer_request(
            video_id=video_id,
            timestamp_sec=playback_time,
            user_query=user_query,
            user_id="usr_yt_zurich_882",
            user_context={"camera_mount": "Sony E-mount", "shoe_size": "US 10", "skin_type": "sensitive"}
        )
        st.session_state.last_response = response
        if response.checkout_payload:
            st.session_state.cumulative_gmv += response.checkout_payload.total_amount
            st.session_state.cumulative_creator_rev += response.checkout_payload.creator_commission_amount
            st.session_state.checkouts_count += 1
            if screen_reader_active:
                st.session_state.aria_announcements.append(f"Purchased product via Google Pay. Transaction ID {response.checkout_payload.transaction_id}")

        st.session_state.chat_history.append({"role": "assistant", "content": response.response_text})
        st.rerun()


# -----------------------------------------------------------------------------
# COLUMN 3: Universal Commerce Protocol (UCP) & Telemetry
# -----------------------------------------------------------------------------
with col_telemetry:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:6px; margin-bottom:10px;">
        <span style="font-size:1.15rem; font-weight:800; color:#FFFFFF;">UCP Inspector</span>
        <span style="width:8px; height:8px; border-radius:50%; background:#00E676; display:inline-block;"></span>
    </div>
    """, unsafe_allow_html=True)

    last_res: PipelineResponse = st.session_state.last_response

    if last_res:
        st.markdown("<h4 style='margin:0 0 6px 0; font-size:0.9rem; font-weight:700; color:#FFF;'>Function Execution Logs</h4>", unsafe_allow_html=True)
        if last_res.ucp_logs:
            for log in last_res.ucp_logs:
                st.code(json.dumps(log, indent=2), language="json")
        else:
            st.caption("No tool calls executed for query.")

        st.markdown("<h4 style='margin:10px 0 6px 0; font-size:0.9rem; font-weight:700; color:#FFF;'>Structured Schemas</h4>", unsafe_allow_html=True)
        with st.expander("CommerceIntent Schema"):
            st.json(last_res.intent.model_dump())

        with st.expander("SafetyCheckResult Schema"):
            st.json(last_res.safety.model_dump())

        if last_res.checkout_payload:
            with st.expander("UCPCheckoutPayload Schema", expanded=True):
                st.json(last_res.checkout_payload.model_dump())
    else:
        st.markdown("""
        <div class="yt-card">
            <div style="font-size:0.85rem; color:#AAAAAA;">
                Execute a 1-click buy or ask a question to inspect live tokenized UCP JSON payloads.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Monetization Telemetry
    st.markdown("<h3 style='margin:0 0 10px 0; font-size:1.1rem; font-weight:800; color:#FFF;'>Monetization Telemetry</h3>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("Gross GMV", f"${st.session_state.cumulative_gmv:,.2f}")
    m2.metric("Creator Split", f"${st.session_state.cumulative_creator_rev:,.2f}")
    st.metric("Total Checkouts", st.session_state.checkouts_count)

    st.markdown("---")

    # Latency Telemetry
    st.markdown("<h3 style='margin:0 0 10px 0; font-size:1.1rem; font-weight:800; color:#FFF;'>Latency Metrics</h3>", unsafe_allow_html=True)
    if last_res and last_res.latency_ms:
        l = last_res.latency_ms
        st.markdown(f"""
        <div class="yt-card">
            <div style="font-size:0.85rem; line-height:1.7; color:#E0E0E0;">
                • Guardrail Check: <code style="color:#00E676;">{l.get('guardrail_ms', 0):.2f} ms</code><br/>
                • Intent Parsing: <code style="color:#00E676;">{l.get('intent_ms', 0):.2f} ms</code><br/>
                • UCP Tool Calling: <code style="color:#00E676;">{l.get('tool_ms', 0):.2f} ms</code><br/>
                • Synthesis: <code style="color:#00E676;">{l.get('synthesis_ms', 0):.2f} ms</code><br/>
                <hr style="border-color:#333; margin:8px 0;"/>
                <strong style="color:#00E676; font-size:0.95rem;">Total Latency: {l.get('total_ms', 0):.2f} ms</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#00E676; font-weight:700; font-size:0.9rem;'>🟢 Ready • Latency &lt; 10 ms</div>", unsafe_allow_html=True)
