import streamlit as st
import requests
import json
import math
import random
import time
from datetime import datetime, timezone
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="விண்வெளி தமிழ்",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# API KEYS  – set via Streamlit secrets or env
# ─────────────────────────────────────────────
NASA_API_KEY  = st.secrets.get("NASA_API_KEY",  os.getenv("NASA_API_KEY",  "DEMO_KEY"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

# ─────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

dark = st.session_state.dark_mode

# ─────────────────────────────────────────────
# CSS – STARS + THEME + FULL STYLING
# ─────────────────────────────────────────────
bg_dark  = "#050a1a"
bg_light = "#dce8ff"
card_dark  = "rgba(10,20,50,0.82)"
card_light = "rgba(255,255,255,0.82)"
text_dark  = "#e8f4ff"
text_light = "#08172e"
accent = "#4fc3f7"
accent2 = "#c084fc"

bg_main   = bg_dark   if dark else bg_light
card_col  = card_dark  if dark else card_light
text_col  = text_dark  if dark else text_light

star_color = "rgba(255,255,255,0.9)" if dark else "rgba(30,80,160,0.4)"

def generate_stars(n=150):
    css = ""
    for i in range(n):
        x  = random.uniform(0,100)
        y  = random.uniform(0,100)
        sz = random.uniform(0.8,2.5)
        delay = random.uniform(0,5)
        dur   = random.uniform(2,6)
        css += f"""
        .star-{i} {{
            position:fixed; left:{x}vw; top:{y}vh;
            width:{sz}px; height:{sz}px;
            background:{star_color};
            border-radius:50%;
            animation: twinkle {dur:.1f}s {delay:.1f}s infinite alternate;
            pointer-events:none; z-index:0;
        }}"""
    return css

random.seed(42)
stars_css = generate_stars(160)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&family=Noto+Sans+Tamil:wght@300;400;600;700&display=swap');

/* ── GLOBAL ─────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Noto Sans Tamil', 'Exo 2', sans-serif !important;
    background: {bg_main} !important;
    color: {text_col} !important;
    transition: background 0.4s, color 0.4s;
}}
.stApp {{ background: transparent !important; }}
section[data-testid="stSidebar"] {{ display:none !important; }}

/* ── STARS ───────────────────────────────── */
{stars_css}

/* ── GRADIENT BG ─────────────────────────── */
.bg-gradient {{
    position: fixed; inset: 0; z-index: -1;
    background: {"radial-gradient(ellipse at 20% 20%, #0d1b4b 0%, #050a1a 60%, #0a0520 100%)" if dark
                 else "radial-gradient(ellipse at 20% 20%, #bcd4f5 0%, #dce8ff 60%, #c8d8ff 100%)"};
    pointer-events: none;
}}

/* ── NEBULA blobs ─────────────────────────── */
.nebula {{
    position:fixed; border-radius:50%; filter:blur(90px);
    pointer-events:none; z-index:0; opacity:{"0.18" if dark else "0.12"};
    animation: drift 12s ease-in-out infinite alternate;
}}
.nebula-1 {{ width:480px;height:480px;left:-100px;top:-80px;
    background:{"#1a237e" if dark else "#90b8ff"}; animation-delay:0s; }}
.nebula-2 {{ width:360px;height:360px;right:-60px;top:30vh;
    background:{"#4a148c" if dark else "#c084fc"}; animation-delay:4s; }}
.nebula-3 {{ width:300px;height:300px;left:30%;bottom:-60px;
    background:{"#006064" if dark else "#67e8f9"}; animation-delay:8s; }}

@keyframes drift {{
    0%  {{ transform: translate(0,0) scale(1); }}
    100%{{ transform: translate(30px,20px) scale(1.08); }}
}}
@keyframes twinkle {{
    0%  {{ opacity:0.1; transform:scale(0.8); }}
    100%{{ opacity:1;   transform:scale(1.2); }}
}}

/* ── TOP NAV ─────────────────────────────── */
.top-nav {{
    position: sticky; top: 0; z-index: 999;
    background: {"rgba(5,10,26,0.92)" if dark else "rgba(200,220,255,0.92)"};
    backdrop-filter: blur(16px);
    border-bottom: 1px solid {"rgba(79,195,247,0.25)" if dark else "rgba(79,195,247,0.4)"};
    padding: 0.6rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
}}
.nav-brand {{
    font-size: 1.4rem; font-weight: 700;
    background: linear-gradient(90deg, {accent}, {accent2});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 0.05em;
}}

/* ── CARDS ───────────────────────────────── */
.card {{
    background: {card_col};
    border: 1px solid {"rgba(79,195,247,0.2)" if dark else "rgba(79,195,247,0.35)"};
    border-radius: 18px;
    padding: 1.6rem;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px {"rgba(0,0,0,0.5)" if dark else "rgba(79,130,200,0.15)"};
    transition: transform 0.25s, box-shadow 0.25s;
    position: relative; z-index: 1;
}}
.card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 16px 48px {"rgba(79,195,247,0.2)" if dark else "rgba(79,130,200,0.3)"};
}}

/* ── SHORTCUT CARDS ─────────────────────── */
.shortcut-card {{
    background: {card_col};
    border: 1px solid {"rgba(192,132,252,0.25)" if dark else "rgba(79,195,247,0.4)"};
    border-radius: 16px;
    padding: 1.4rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    backdrop-filter: blur(14px);
    position: relative; z-index:1;
}}
.shortcut-card:hover {{
    border-color: {accent};
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 40px {"rgba(79,195,247,0.3)" if dark else "rgba(79,195,247,0.4)"};
}}
.shortcut-icon {{ font-size: 2.8rem; margin-bottom: 0.5rem; }}
.shortcut-title {{ font-size: 1.05rem; font-weight:700; color:{accent}; margin-bottom:0.4rem; }}
.shortcut-desc {{ font-size: 0.82rem; opacity:0.78; line-height:1.5; }}

/* ── ISS DISPLAY ─────────────────────────── */
.iss-stat {{
    background: {card_col};
    border: 1px solid {"rgba(79,195,247,0.2)" if dark else "rgba(79,195,247,0.35)"};
    border-radius:12px; padding:1rem 1.4rem;
    backdrop-filter:blur(10px); text-align:center;
    position:relative; z-index:1;
}}
.iss-stat-value {{ font-size:1.5rem; font-weight:700; color:{accent}; }}
.iss-stat-label {{ font-size:0.78rem; opacity:0.7; margin-top:0.2rem; }}

/* ── GALLERY ─────────────────────────────── */
.gallery-img-wrap {{
    border-radius: 14px; overflow:hidden;
    border: 1px solid {"rgba(79,195,247,0.2)" if dark else "rgba(79,130,200,0.3)"};
    box-shadow: 0 6px 24px {"rgba(0,0,0,0.5)" if dark else "rgba(0,0,0,0.12)"};
    position:relative; z-index:1; transition: transform 0.3s;
}}
.gallery-img-wrap:hover {{ transform: scale(1.025); }}
.gallery-caption {{
    background: {"rgba(5,10,26,0.85)" if dark else "rgba(255,255,255,0.9)"};
    padding: 0.7rem 1rem; font-size:0.8rem; line-height:1.5;
    border-top: 1px solid {"rgba(79,195,247,0.15)" if dark else "rgba(79,130,200,0.2)"};
}}

/* ── NEWS GRID ───────────────────────────── */
.news-card {{
    background: {card_col};
    border: 1px solid {"rgba(79,195,247,0.18)" if dark else "rgba(79,130,200,0.3)"};
    border-radius: 14px; overflow:hidden;
    backdrop-filter: blur(12px);
    transition: transform 0.3s;
    position:relative; z-index:1;
    height: 100%;
}}
.news-card:hover {{ transform: translateY(-4px); }}
.news-tag {{
    display:inline-block; padding:0.2rem 0.7rem; border-radius:20px;
    font-size:0.72rem; font-weight:600; margin-bottom:0.5rem;
    background: linear-gradient(90deg,{accent},{accent2});
    color:#fff;
}}
.news-title {{ font-size:0.92rem; font-weight:600; line-height:1.5; margin-bottom:0.4rem; }}
.news-desc  {{ font-size:0.78rem; opacity:0.72; line-height:1.5; }}
.news-date  {{ font-size:0.7rem; opacity:0.55; margin-top:0.5rem; }}

/* ── CHAT ────────────────────────────────── */
.chat-bubble-user {{
    background: linear-gradient(135deg, {accent2}, #7c3aed);
    color: #fff; border-radius: 18px 18px 4px 18px;
    padding: 0.8rem 1.1rem; margin: 0.5rem 0;
    max-width: 78%; margin-left:auto; font-size:0.88rem;
    position:relative; z-index:1;
}}
.chat-bubble-bot {{
    background: {card_col};
    border: 1px solid {"rgba(79,195,247,0.25)" if dark else "rgba(79,195,247,0.4)"};
    color: {text_col}; border-radius: 18px 18px 18px 4px;
    padding: 0.8rem 1.1rem; margin: 0.5rem 0;
    max-width: 78%; font-size:0.88rem; line-height:1.6;
    position:relative; z-index:1;
}}

/* ── SECTION HEADINGS ────────────────────── */
.section-title {{
    font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(90deg, {accent}, {accent2});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}}
.section-subtitle {{ font-size:0.9rem; opacity:0.65; margin-bottom:1.5rem; }}

/* ── STREAMLIT OVERRIDES ─────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {accent}, {accent2}) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight:600 !important;
    padding: 0.5rem 1.4rem !important; transition: opacity 0.2s !important;
}}
.stButton > button:hover {{ opacity: 0.85 !important; }}
.stTextInput > div > div > input {{
    background: {card_col} !important; color: {text_col} !important;
    border: 1px solid {"rgba(79,195,247,0.3)" if dark else "rgba(79,130,200,0.4)"} !important;
    border-radius: 10px !important;
}}
div[data-testid="stTabs"] button {{
    color: {text_col} !important; font-family:'Noto Sans Tamil',sans-serif !important;
    font-size:0.95rem !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom: 2px solid {accent} !important;
}}
div[data-testid="stMetricValue"] {{ color:{accent} !important; }}
.stSpinner > div {{ border-top-color: {accent} !important; }}

/* ── TOGGLE ─────────────────────────────── */
.toggle-wrap {{
    display:flex; align-items:center; gap:0.5rem;
    font-size:0.85rem;
}}
</style>

<!-- Background layers -->
<div class="bg-gradient"></div>
<div class="nebula nebula-1"></div>
<div class="nebula nebula-2"></div>
<div class="nebula nebula-3"></div>
""" + "".join(f'<div class="star-{i}"></div>' for i in range(160)),
unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TOP NAVIGATION BAR
# ─────────────────────────────────────────────
col_brand, col_toggle = st.columns([6,1])
with col_brand:
    st.markdown('<div class="nav-brand">🚀 விண்வெளி தமிழ் — Space Tamil</div>', unsafe_allow_html=True)
with col_toggle:
    mode_label = "🌙 இருள்" if dark else "☀️ வெளிச்சம்"
    if st.button(mode_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tabs = st.tabs(["🏠 முகப்பு", "🛰️ ISS கண்காணிப்பு", "🖼️ தொகுப்பகம்", "📰 விண்வெளி செய்திகள்", "👩‍🚀 விண்வெளி உதவியாளர்"])

# ══════════════════════════════════════════════
# TAB 1 – HOME
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem;">
        <div style="font-size:3.5rem;">🌌</div>
        <h1 class="section-title" style="font-size:2.4rem;">விண்வெளி தமிழ்-க்கு வரவேற்கிறோம்!</h1>
        <p class="section-subtitle" style="font-size:1rem; max-width:680px; margin:auto;">
            அண்டவெளியின் அதிசயங்களை தமிழில் ஆராயுங்கள் — இது உங்கள் விண்வெளி பயண வழிகாட்டி
        </p>
    </div>
    """, unsafe_allow_html=True)

    # About space
    st.markdown(f"""
    <div class="card" style="margin-bottom:1.5rem;">
        <div style="font-size:1.3rem; font-weight:700; color:{accent}; margin-bottom:0.8rem;">🌠 விண்வெளி என்றால் என்ன?</div>
        <p style="line-height:2; font-size:0.95rem; opacity:0.88;">
        விண்வெளி என்பது பூமிக்கு அப்பால் பரந்து கிடக்கும் எல்லையற்ற அண்டம். சூரியன், நட்சத்திரங்கள், கிரகங்கள், 
        நெபுலாக்கள் மற்றும் கருந்துளைகள் நிறைந்த இந்த அண்டவெளி, மனித அறிவின் மிகப்பெரிய சவால்களில் ஒன்றாகும். 
        தோராயமாக 13.8 பில்லியன் ஆண்டுகளுக்கு முன் நடந்த பிக் பேங் என்ற மாபெரும் வெடிப்பு மூலம் இந்த பிரபஞ்சம் 
        உருவானது என்று விஞ்ஞானிகள் கண்டறிந்துள்ளனர். நாம் இன்று காணும் நட்சத்திரங்கள், கண்களுக்கு தெரியாத ஒளியற்ற 
        இடங்களில் மறைந்திருக்கும் ரகசியங்கள் — விண்வெளி என்னும் கடல் இன்னும் ஆராயப்படாத உலகம்!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # About the app
    st.markdown(f"""
    <div class="card" style="margin-bottom:2rem;">
        <div style="font-size:1.3rem; font-weight:700; color:{accent2}; margin-bottom:0.8rem;">🎯 இந்த செயலி பற்றி</div>
        <p style="line-height:2; font-size:0.95rem; opacity:0.88;">
        <b>விண்வெளி தமிழ்</b> என்பது தமிழ் மொழியில் விண்வெளி அறிவியலை எல்லோருக்கும் எளிதாக புரியும்படி கொண்டு சேர்க்கும் 
        ஒரு செயலி. NASA-வின் APOD படங்கள், சர்வதேச விண்வெளி நிலையம் (ISS) இன் நேரடி தகவல்கள், 
        சமீபத்திய விண்வெளி செய்திகள் மற்றும் ஒரு தமிழ் பேசும் விண்வெளி வீரர் உதவியாளர் — 
        அனைத்தும் ஒரே இடத்தில்! இந்த செயலியின் நோக்கம்: 
        <b>தமிழ் மொழியில் விஞ்ஞான ஆர்வத்தை மேம்படுத்துவது, குழந்தைகள் முதல் பெரியவர்கள் வரை 
        அனைவருக்கும் விண்வெளி கனவை அருகில் கொண்டு வருவது.</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Shortcut cards
    st.markdown(f'<div class="section-title">⚡ விரைவு செல்லிகள்</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">கீழுள்ள பகுதிகளுக்கு நேரடியாக செல்லுங்கள்</div>', unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    shortcuts = [
        (sc1, "🛰️", "ISS கண்காணிப்பு", "சர்வதேச விண்வெளி நிலையம் இப்போது எங்கே உள்ளது என்று நேரடியாக பாருங்கள்"),
        (sc2, "🖼️", "தொகுப்பகம்", "NASA-வின் அழகான விண்வெளி படங்களை ரசியுங்கள்"),
        (sc3, "📰", "விண்வெளி செய்திகள்", "சுடச்சுட விண்வெளி செய்திகள் — கோள்கள், நட்சத்திரங்கள், செவ்வாய் மற்றும் சந்திரன்"),
        (sc4, "👩‍🚀", "விண்வெளி உதவியாளர்", "தமிழில் பேசும் AI விண்வெளி வீரருடன் உரையாடுங்கள்"),
    ]
    for col, icon, title, desc in shortcuts:
        with col:
            st.markdown(f"""
            <div class="shortcut-card">
                <div class="shortcut-icon">{icon}</div>
                <div class="shortcut-title">{title}</div>
                <div class="shortcut-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 – ISS LOCATOR
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown(f'<div class="section-title">🛰️ சர்வதேச விண்வெளி நிலையம் (ISS)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">நேர்மையான நிலை • வேகம் • கூட்டுறவு</div>', unsafe_allow_html=True)

    # Simulated orbital position
    now_ts = time.time()
    # ISS orbits every ~92 minutes; simulate lat/lon
    orbit_period = 92 * 60
    phase = (now_ts % orbit_period) / orbit_period * 2 * math.pi
    iss_lat = 51.6 * math.sin(phase * 1.1)
    iss_lon = ((now_ts / 420) % 360) - 180
    iss_alt = 408.3 + 2.1 * math.sin(phase * 0.7)
    iss_spd = 27600 + 120 * math.sin(phase)
    iss_orbit_num = int(now_ts / (92 * 60)) + 3000
    inclination = 51.6

    # Crew list (actual current-ish crew)
    crew = [
        ("Oleg Kononenko", "🇷🇺", "கமாண்டர்"),
        ("Nikolai Chub", "🇷🇺", "விண்வெளி வீரர்"),
        ("Tracy Dyson", "🇺🇸", "விண்வெளி வீரர்"),
        ("Matthew Dominick", "🇺🇸", "விண்வெளி வீரர்"),
        ("Michael Barratt", "🇺🇸", "விண்வெளி வீரர்"),
        ("Jeanette Epps", "🇺🇸", "விண்வெளி வீரர்"),
        ("Alexander Grebenkin", "🇷🇺", "விண்வெளி வீரர்"),
    ]

    # Stats row
    c1,c2,c3,c4 = st.columns(4)
    stats = [
        ("🌐 நிலை (Lat)", f"{iss_lat:.2f}°"),
        ("🌐 நிலை (Lon)", f"{iss_lon:.2f}°"),
        ("⬆️ உயரம்", f"{iss_alt:.1f} கி.மீ"),
        ("💨 வேகம்", f"{iss_spd:.0f} கி.மீ/மணி"),
    ]
    for col,(lbl,val) in zip([c1,c2,c3,c4], stats):
        with col:
            st.markdown(f"""<div class="iss-stat">
                <div class="iss-stat-value">{val}</div>
                <div class="iss-stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c5,c6,c7,c8 = st.columns(4)
    stats2 = [
        ("🔄 சுற்று எண்", f"#{iss_orbit_num}"),
        ("📐 சாய்வு", f"{inclination}°"),
        ("⏱️ சுற்று காலம்", "~92 நிமிடம்"),
        ("👨‍🚀 குழு உறுப்பினர்", f"{len(crew)} பேர்"),
    ]
    for col,(lbl,val) in zip([c5,c6,c7,c8], stats2):
        with col:
            st.markdown(f"""<div class="iss-stat">
                <div class="iss-stat-value">{val}</div>
                <div class="iss-stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Map + Crew side by side
    map_col, crew_col = st.columns([3,2])

    with map_col:
        st.markdown(f'<div style="font-weight:600;color:{accent};margin-bottom:0.5rem;">🗺️ உலக வரைபடத்தில் ISS நிலை</div>', unsafe_allow_html=True)
        try:
            import folium
            from streamlit_folium import st_folium

            m = folium.Map(
                location=[iss_lat, iss_lon],
                zoom_start=2,
                tiles="CartoDB dark_matter" if dark else "CartoDB positron",
            )
            # ISS marker
            folium.Marker(
                [iss_lat, iss_lon],
                popup=f"ISS\nLat: {iss_lat:.2f}° Lon: {iss_lon:.2f}°",
                tooltip="🛰️ ISS இப்போது இங்கே!",
                icon=folium.DivIcon(html="""
                    <div style="font-size:28px;margin:-14px 0 0 -14px;
                    filter:drop-shadow(0 0 8px #4fc3f7);">🛰️</div>""")
            ).add_to(m)

            # Ground track dots
            for i in range(1, 20):
                past_phase = phase - (i * 0.05)
                plat = 51.6 * math.sin(past_phase * 1.1)
                plon = iss_lon - i * 4
                if plon < -180: plon += 360
                folium.CircleMarker(
                    [plat, plon], radius=3,
                    color="#4fc3f7", fill=True, fill_opacity=0.3-i*0.012
                ).add_to(m)

            st_folium(m, width=None, height=380)
        except Exception:
            # Fallback simple display
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:2rem;">
                <div style="font-size:3rem;">🛰️</div>
                <div style="color:{accent};font-size:1.1rem;margin-top:1rem;">
                    தற்போதைய ISS நிலை:<br>
                    <b>Lat: {iss_lat:.2f}° | Lon: {iss_lon:.2f}°</b>
                </div>
                <div style="opacity:0.6;margin-top:0.5rem;font-size:0.8rem;">
                    (folium நிறுவ: pip install folium streamlit-folium)
                </div>
            </div>""", unsafe_allow_html=True)

    with crew_col:
        st.markdown(f'<div style="font-weight:600;color:{accent2};margin-bottom:0.8rem;">👨‍🚀 குழு உறுப்பினர்கள்</div>', unsafe_allow_html=True)
        for name, flag, role in crew:
            st.markdown(f"""
            <div class="card" style="margin-bottom:0.6rem;padding:0.8rem 1rem;">
                <span style="font-size:1.2rem;">{flag}</span>
                <span style="font-weight:600;margin-left:0.5rem;">{name}</span><br>
                <span style="font-size:0.78rem;opacity:0.65;margin-left:1.7rem;">{role}</span>
            </div>""", unsafe_allow_html=True)

        if st.button("🔄 நிலையை புதுப்பி"):
            st.rerun()

# ══════════════════════════════════════════════
# TAB 3 – GALLERY
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown(f'<div class="section-title">🖼️ விண்வெளி தொகுப்பகம்</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">NASA APOD — அன்றாட விண்வெளி புகைப்படங்கள்</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def fetch_apod(count=12, api_key="DEMO_KEY"):
        url = f"https://api.nasa.gov/planetary/apod?count={count}&api_key={api_key}&thumbs=true"
        try:
            r = requests.get(url, timeout=10)
            return r.json() if r.status_code == 200 else []
        except:
            return []

    with st.spinner("NASA படங்கள் ஏற்றப்படுகின்றன..."):
        apod_items = fetch_apod(12, NASA_API_KEY)

    if not apod_items:
        # Fallback simulated gallery
        apod_items = [
            {"title": "நட்சத்திர நாசல் — Pillars of Creation", "date": "2024-01-15",
             "explanation": "கழுகு நெபுலாவில் உள்ள மாபெரும் வாயு மற்றும் தூசி தூண்கள். புதிய நட்சத்திரங்கள் இங்கு உருவாகின்றன.",
             "url": "https://upload.wikimedia.org/wikipedia/commons/6/68/Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg",
             "media_type": "image"},
        ]
        st.info("NASA API-ஐ அணுக முடியவில்லை. மாதிரி படங்கள் காட்டப்படுகின்றன.")

    # Filter only images
    images = [i for i in apod_items if isinstance(i, dict) and i.get("media_type") == "image"]

    if images:
        num_cols = 3
        rows = [images[i:i+num_cols] for i in range(0,len(images),num_cols)]
        for row in rows:
            cols = st.columns(num_cols)
            for col, item in zip(cols, row):
                with col:
                    img_url = item.get("hdurl") or item.get("url","")
                    title = item.get("title","தலைப்பு இல்லை")
                    date  = item.get("date","")
                    expl  = item.get("explanation","")[:160] + "..."
                    st.markdown(f"""
                    <div class="gallery-img-wrap">
                        <img src="{img_url}" style="width:100%;height:200px;object-fit:cover;display:block;"
                            onerror="this.style.display='none'"/>
                        <div class="gallery-caption">
                            <div style="font-weight:600;color:{accent};margin-bottom:0.3rem;">{title}</div>
                            <div style="opacity:0.75;">{expl}</div>
                            <div style="opacity:0.5;margin-top:0.4rem;font-size:0.7rem;">📅 {date}</div>
                        </div>
                    </div><br>""", unsafe_allow_html=True)
    else:
        st.warning("படங்கள் கிடைக்கவில்லை. API விசையை சரிபாருங்கள்.")

# ══════════════════════════════════════════════
# TAB 4 – SPACE NEWS
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown(f'<div class="section-title">📰 விண்வெளி செய்திகள்</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">சுடச்சுட விண்வெளி செய்திகள் — சிமுலேட்டட் தரவு</div>', unsafe_allow_html=True)

    news_data = {
        "☄️ விண்கற்கள்": [
            {
                "title": "2024 YR4 — புவியை நோக்கி வருகிறதா?",
                "desc": "NASA வானியலாளர்கள் 2024 YR4 என்ற விண்கல் 2032-ல் புவியை நெருங்கலாம் என கண்காணிக்கின்றனர். இது 45-100 மீட்டர் அகலம் கொண்டது.",
                "date": "மார்ச் 2025", "emoji": "☄️"
            },
            {
                "title": "Apophis 2029-ல் புவியை கடக்கும்",
                "desc": "370 மீட்டர் அகலமுள்ள Apophis விண்கல் 2029 ஏப்ரல் 13 அன்று மிக அருகில் கடக்கும். இது தொலைக்காட்சியிலேயே தெரியும்!",
                "date": "பிப்ரவரி 2025", "emoji": "🌍"
            },
        ],
        "⭐ நட்சத்திரங்கள்": [
            {
                "title": "Betelgeuse மின்னலுடன் பிரகாசிக்கிறது",
                "desc": "ஓரியன் மண்டலத்தில் உள்ள Betelgeuse நட்சத்திரம் எதிர்பார்த்ததை விட அதிகமாக பிரகாசிக்கிறது. விஞ்ஞானிகள் ஆர்வமாக கவனிக்கிறார்கள்.",
                "date": "ஜனவரி 2025", "emoji": "✨"
            },
            {
                "title": "புதிய நட்சத்திர வழிமாப்பு கண்டுபிடிப்பு",
                "desc": "James Webb தொலைநோக்கி 13.4 பில்லியன் ஒளியாண்டு தொலைவில் ஒரு பழைய நட்சத்திர குழுவை கண்டறிந்துள்ளது.",
                "date": "மார்ச் 2025", "emoji": "🔭"
            },
        ],
        "🔴 செவ்வாய்": [
            {
                "title": "Perseverance — நீர் சுவடுகள் கண்டறிந்தது",
                "desc": "NASA-வின் Perseverance ரோவர் செவ்வாயில் பழங்கால நீர் ஆறுகளின் தடங்களை கண்டறிந்துள்ளது. இது உயிர் இருந்திருக்கலாம் என்ற நம்பிக்கையை அளிக்கிறது.",
                "date": "பிப்ரவரி 2025", "emoji": "💧"
            },
            {
                "title": "SpaceX Starship — செவ்வாய் பயணம் 2026",
                "desc": "Elon Musk-ன் SpaceX நிறுவனம் 2026-ல் Starship மூலம் செவ்வாய்க்கு சரக்கு அனுப்ப திட்டமிட்டுள்ளது.",
                "date": "ஜனவரி 2025", "emoji": "🚀"
            },
        ],
        "🌕 சந்திரன்": [
            {
                "title": "Artemis III — சந்திரன் தென் துருவம்",
                "desc": "NASA-வின் Artemis III திட்டம் 2026-ல் பெண் விண்வெளி வீரரை சந்திரனில் இறக்க உள்ளது. தென் துருவத்தில் பனிநீர் ஆராய்ச்சி நடைபெறும்.",
                "date": "மார்ச் 2025", "emoji": "👩‍🚀"
            },
            {
                "title": "சந்திரயான்-4 — இந்தியாவின் அடுத்த பயணம்",
                "desc": "ISRO சந்திரயான்-4 திட்டத்தை அறிவித்துள்ளது. இது சந்திரனில் இருந்து மண் மாதிரிகளை பூமிக்கு கொண்டு வரும்.",
                "date": "பிப்ரவரி 2025", "emoji": "🌙"
            },
        ],
    }

    for category, articles in news_data.items():
        st.markdown(f"""<div style="font-size:1.15rem;font-weight:700;color:{accent};
                        margin:1.5rem 0 0.8rem; display:flex;align-items:center;gap:0.5rem;">
                        {category}
                    </div>""", unsafe_allow_html=True)
        cols = st.columns(len(articles))
        for col, art in zip(cols, articles):
            with col:
                st.markdown(f"""
                <div class="news-card">
                    <div style="padding:1.1rem;">
                        <div style="font-size:2rem;margin-bottom:0.5rem;">{art['emoji']}</div>
                        <div class="news-title">{art['title']}</div>
                        <div class="news-desc">{art['desc']}</div>
                        <div class="news-date">📅 {art['date']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 – ASTRONAUT ASSISTANT
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown(f'<div class="section-title">👩‍🚀 விண்வெளி உதவியாளர்</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">தமிழில் பேசும் AI விண்வெளி வீரர் — உங்கள் கேள்விகளுக்கு பதில் தருவேன்!</div>', unsafe_allow_html=True)

    chat_col, img_col = st.columns([3, 1])

    with img_col:
        # Robot astronaut image placeholder
        robot_img_path = "D:\\Mocoworks\\repos\\streamlit tamil astronomy\\robot.png"
        if os.path.exists(robot_img_path):
            st.image(robot_img_path, use_container_width=True)
        else:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:2rem 1rem;">
                <div style="font-size:5rem;">🤖</div>
                <div style="color:{accent};font-weight:600;margin-top:0.8rem;font-size:0.9rem;">
                    ASTRO-தமிழன்
                </div>
                <div style="opacity:0.6;font-size:0.75rem;margin-top:0.5rem;">
                    உங்கள் AI விண்வெளி வீரர்
                </div>
                <div style="opacity:0.45;font-size:0.65rem;margin-top:1rem;">
                    Robot படத்தை<br>பதிவேற்றுங்கள்
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card" style="margin-top:1rem;font-size:0.78rem;opacity:0.75;text-align:center;">
            🚀 ISS-ல் இருந்து<br>
            உங்களுடன் பேசுகிறேன்!<br><br>
            <span style="color:{accent};">தமிழிலேயே கேளுங்கள்</span>
        </div>""", unsafe_allow_html=True)

    with chat_col:
        # Chat history display
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(f"""
                <div class="chat-bubble-bot">
                    வணக்கம்! நான் ASTRO-தமிழன், உங்கள் AI விண்வெளி வீரர். 
                    சர்வதேச விண்வெளி நிலையத்தில் இருந்து உங்களுடன் பேசுகிறேன்! 🚀<br><br>
                    விண்வெளி பற்றி என்ன கேள்வியும் கேளுங்கள் — தமிழிலோ, ஆங்கிலத்திலோ கேட்கலாம்.
                    நான் தமிழிலேயே பதில் சொல்வேன்! 🌌
                </div>""", unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

        # Input
        user_input = st.text_input(
            "உங்கள் கேள்வி:",
            placeholder="விண்வெளி பற்றி கேளுங்கள்... (e.g. ISS எப்படி இருக்கும்?)",
            key="chat_input",
            label_visibility="collapsed"
        )

        send_col, clear_col = st.columns([3,1])
        with send_col:
            send = st.button("📨 அனுப்பு", use_container_width=True)
        with clear_col:
            if st.button("🗑️ அழி", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if send and user_input.strip():
            st.session_state.chat_history.append({"role":"user","content":user_input})

            def call_openai(messages, api_key):
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 400,
                    "temperature": 0.85,
                }
                r = requests.post(url, headers=headers, json=body, timeout=20)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                return None

            system_prompt = """நீ ASTRO-தமிழன் என்ற AI விண்வெளி வீரர். நீ சர்வதேச விண்வெளி நிலையத்தில் (ISS) இருந்து பேசுகிறாய்.
எப்போதும் தமிழிலேயே பதில் சொல் (user ஆங்கிலத்தில் கேட்டாலும் தமிழிலேயே பதில் சொல்).
நீ உற்சாகமான, நட்பான, அறிவியல் ஆர்வமுள்ள விண்வெளி வீரர். ISS வாழ்க்கை, விண்வெளி அறிவியல், கிரகங்கள், நட்சத்திரங்கள் பற்றி சுவாரஸ்யமாக விளக்கு.
சிறு emoji சேர்க்கலாம். பதில்கள் 3-5 வாக்கியங்களில் இருக்கட்டும்."""

            if OPENAI_API_KEY:
                messages = [{"role":"system","content":system_prompt}]
                for m in st.session_state.chat_history[:-1]:
                    messages.append(m)
                messages.append({"role":"user","content":user_input})

                with st.spinner("ASTRO-தமிழன் பதில் தயாரிக்கிறார்..."):
                    reply = call_openai(messages, OPENAI_API_KEY)
                    if not reply:
                        reply = "மன்னிக்கவும், தற்போது இணைப்பில் சிக்கல் உள்ளது. சிறிது நேரம் கழித்து முயற்சிக்கவும்! 🛰️"
            else:
                # Simulated replies
                simulated = {
                    "iss": "ISS-ல் வாழ்க்கை மிகவும் சுவாரஸ்யமாக உள்ளது! 🚀 நாங்கள் ஒவ்வொரு 90 நிமிடத்திலும் பூமியை ஒரு முறை சுற்றுகிறோம். இங்கே எல்லாமே மிதக்கும் — தண்ணீர், உணவு, நாங்களும்கூட! நாளொன்றுக்கு 16 சூரிய உதயங்களை நாங்கள் பார்க்கிறோம்.",
                    "mars": "செவ்வாய் கிரகம் பூமியை விட 6 மடங்கு சிறியது. 🔴 அங்கு ஒரு நாள் 24 மணி 37 நிமிடம். Perseverance ரோவர் இப்போது அங்கு ஆராய்ச்சி செய்கிறது. எதிர்காலத்தில் மனிதர்கள் செவ்வாயில் வாழலாம் என்று விஞ்ஞானிகள் நம்புகிறார்கள்!",
                    "moon": "சந்திரன் பூமியிலிருந்து சராசரியாக 3,84,400 கி.மீ தொலைவில் உள்ளது. 🌕 1969-ல் Neil Armstrong முதன்முதலில் சந்திரனில் கால் வைத்தார். இந்தியாவின் சந்திரயான்-3 தென் துருவத்தில் தரையிறங்கி வரலாறு படைத்தது!",
                    "star": "நட்சத்திரங்கள் வாயு மற்றும் தூளால் ஆனவை. ⭐ நம் சூரியன் ஒரு நட்சத்திரமே! பிரபஞ்சத்தில் கோடானகோடி நட்சத்திரங்கள் உள்ளன. Betelgeuse நட்சத்திரம் சூரியனை விட 700 மடங்கு பெரியது!",
                }
                reply = None
                q_lower = user_input.lower()
                for k,v in simulated.items():
                    if k in q_lower:
                        reply = v
                        break
                if not reply:
                    reply = f"மிகவும் சுவாரஸ்யமான கேள்வி! 🌌 ISS-லிருந்து நான் இதை சொல்ல விரும்புகிறேன்: விண்வெளி ஆராய்ச்சி மனிதகுலத்தின் மிகப்பெரிய சாதனை. OpenAI API விசை அமைக்கப்பட்டால் விரிவான பதில் தருவேன்!"

            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.rerun()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;opacity:0.5;font-size:0.75rem;padding:1rem 0;">
    🚀 விண்வெளி தமிழ் | NASA APOD API மூலம் இயங்குகிறது | தமிழில் விண்வெளி ஆராய்ச்சி<br>
    Made with ❤️ for Tamil Space Enthusiasts
</div>
""", unsafe_allow_html=True)
