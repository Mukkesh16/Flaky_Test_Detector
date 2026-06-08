"""
ui_components.py
Reusable UI building blocks for the Flaky Test Detector & Explainer dashboard.
"""

import streamlit as st

# Color Palette
PRIMARY   = "#0FF4C6"
ACCENT    = "#FF3CAC"
WARN      = "#FFD166"
DANGER    = "#FF4D6D"
BG_DEEP   = "#0A0E1A"
BG_CARD   = "#111827"
BG_LIGHT  = "#1C2333"
TEXT_MAIN = "#E8EDF5"
TEXT_MUTED= "#6B7A99"

def inject_global_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        background: {BG_DEEP} !important;
        color: {TEXT_MAIN};
        font-family: 'DM Sans', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background: {BG_CARD} !important;
        border-right: 1px solid #1E2D45;
    }}
    [data-testid="stSidebar"] * {{ color: {TEXT_MAIN} !important; }}
    [data-testid="stHeader"] {{ display: none; }}

    /* Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #00C8A0 100%);
        color: {BG_DEEP} !important;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px {PRIMARY}55;
        border: none;
        color: {BG_DEEP} !important;
    }}

    /* Input & Textarea Styling */
    .stTextInput input, .stTextArea textarea {{
        background: {BG_LIGHT} !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid #2A3550 !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 0.75rem 1rem !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 2px {PRIMARY}33 !important;
    }}

    /* Selectbox Styling */
    div[data-baseweb="select"] > div {{
        background: {BG_LIGHT} !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid #2A3550 !important;
        border-radius: 8px !important;
    }}

    /* Chat Input Box (New!) */
    [data-testid="stChatInput"] {{
        background: {BG_CARD} !important;
        border: 1px solid #2A3550 !important;
        border-radius: 12px;
    }}
    [data-testid="stChatInput"] textarea {{
        color: {TEXT_MAIN} !important;
        background: transparent !important;
    }}
    
    /* Native Chat Bubbles (New!) */
    [data-testid="stChatMessageContent"] {{
        background: {BG_CARD};
        border: 1px solid #1E2D45;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        font-size: 0.95rem;
        line-height: 1.6;
        color: {TEXT_MAIN};
    }}
    [data-testid="chatAvatarIcon-user"] {{
        background-color: {ACCENT} !important;
    }}
    [data-testid="chatAvatarIcon-assistant"] {{
        background-color: {PRIMARY} !important;
    }}

    /* Metric Cards */
    [data-testid="metric-container"] {{
        background: {BG_CARD};
        border: 1px solid #1E2D45;
        border-radius: 12px;
        padding: 1.2rem;
        transition: transform 0.2s;
    }}
    [data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}

    /* DataFrame Styling */
    .stDataFrame {{ border-radius: 12px; overflow: hidden; border: 1px solid #1E2D45; }}
    thead tr th {{ background: {BG_LIGHT} !important; color: {PRIMARY} !important;
                   font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; }}
    tbody tr:hover {{ background: #1A2438 !important; }}

    /* Progress Bar */
    .stProgress > div > div > div > div {{ background: linear-gradient(90deg, {PRIMARY}, {ACCENT}) !important; }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: {BG_CARD} !important;
        border: 1px solid #1E2D45 !important;
        border-radius: 8px !important;
        color: {TEXT_MAIN} !important;
        font-family: 'Space Mono', monospace !important;
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {BG_DEEP}; }}
    ::-webkit-scrollbar-thumb {{ background: #2A3550; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {PRIMARY}88; }}
    
    /* Animations */
    @keyframes fadeSlideIn {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-in {{ animation: fadeSlideIn 0.45s cubic-bezier(0.4, 0, 0.2, 1) both; }}

    .nav-label {{
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        padding: 0.8rem 0 0.5rem 0.2rem;
    }}
    
    /* Skeleton Loader Animation */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    .skeleton {{
        animation: shimmer 2s infinite linear;
        background: linear-gradient(to right, {BG_CARD} 4%, #1A2438 25%, {BG_CARD} 36%);
        background-size: 1000px 100%;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_topbar(page_title: str = ""):
    st.markdown(f"""
    <div class="animate-in" style="
        display:flex; align-items:center; justify-content:space-between;
        padding:1rem 1.8rem; margin-bottom:1.5rem;
        background:linear-gradient(90deg,{BG_CARD},{BG_DEEP});
        border-bottom:1px solid #1E2D45; border-radius:0 0 16px 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
      <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:40px;height:40px;border-radius:10px;
                    background:linear-gradient(135deg,{PRIMARY},{ACCENT});
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.2rem;box-shadow: 0 4px 10px {PRIMARY}44;">⚡</div>
        <div>
          <div style="font-family:'Space Mono',monospace;font-weight:700;
                      font-size:1.1rem;letter-spacing:0.05em;">
            FLAKY<span style="color:{PRIMARY}">TEST</span>
            <span style="color:{TEXT_MUTED}">DETECTOR</span>
          </div>
          <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:-2px;">
            Powered by Ollama (Local)
          </div>
        </div>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.8rem;
                  color:{PRIMARY};background:{PRIMARY}18;
                  border:1px solid {PRIMARY}44;border-radius:20px;
                  padding:0.3rem 1rem;">
        {page_title}
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1.5rem 0.5rem 0.5rem;">
          <div style="font-family:'Space Mono',monospace;font-size:1.2rem;
                      font-weight:700;color:{TEXT_MAIN};">⚡ FlakyDetect</div>
          <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:4px;">
            Local AI Powered
          </div>
        </div>
        <hr style="border-color:#1E2D45;margin:1rem 0;">
        <div class="nav-label">Navigation</div>
        """, unsafe_allow_html=True)

        pages = {
            "📂 Upload Data": "upload",
            "📊 Detection Results": "table",
            "🤖 AI Explanations": "ai",
            "⚙ Agent Execution": "agent",
            "📜 Investigation History": "history",
            "📥 Download Reports": "download",
            "💬 Chat With Data": "chat",
        }
        selection = st.radio("", list(pages.keys()), label_visibility="collapsed")
        
        st.markdown("<hr style='border-color:#1E2D45;margin:1.5rem 0 1rem;'>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{BG_LIGHT};border:1px solid #1E2D45;border-radius:10px;
                    padding:1rem;margin-top:0.5rem;">
          <div style="font-family:'Space Mono',monospace;font-size:0.75rem;
                      color:{TEXT_MUTED};letter-spacing:0.1em;">AI ENGINE</div>
          <div style="display:flex;align-items:center;gap:8px;margin-top:8px;">
            <div style="width:8px;height:8px;border-radius:50%;
                        background:{PRIMARY};box-shadow: 0 0 8px {PRIMARY};"></div>
            <span style="font-size:0.85rem;color:{TEXT_MAIN};font-weight:500;">Ollama Local</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        return pages[selection]


def section_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="animate-in" style="margin-bottom:1.5rem;">
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.6rem;background:{BG_CARD};padding:8px;border-radius:10px;border:1px solid #1E2D45;">{icon}</span>
        <div>
          <h2 style="margin:0;font-family:'Space Mono',monospace;font-size:1.3rem;
                     font-weight:700;color:{TEXT_MAIN};">{title}</h2>
          {"<p style='margin:4px 0 0;font-size:0.9rem;color:"+TEXT_MUTED+";'>"+subtitle+"</p>" if subtitle else ""}
        </div>
      </div>
      <div style="height:2px;background:linear-gradient(90deg,{PRIMARY}88,transparent);
                  border-radius:2px;margin-top:14px;"></div>
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: list):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        color = m.get("color", PRIMARY)
        col.markdown(f"""
        <div class="animate-in" style="background:{BG_CARD};border:1px solid #1E2D45;
                    border-left:4px solid {color};border-radius:12px;padding:1.2rem;
                    height:100%;display:flex;flex-direction:column;justify-content:center;">
          <div style="font-size:0.75rem;color:{TEXT_MUTED};font-family:'Space Mono',monospace;
                      letter-spacing:0.08em;text-transform:uppercase;">{m['label']}</div>
          <div style="font-size:1.8rem;font-weight:700;color:{color};
                      font-family:'Space Mono',monospace;line-height:1.2;margin-top:6px;">{m['value']}</div>
        </div>
        """, unsafe_allow_html=True)


def score_badge(score: float) -> str:
    # Convert flakiness score (0.0 - 1.0) to percentage (0 - 100)
    score_pct = int(score * 100)
    if score >= 0.75:
        color, label = DANGER, "HIGH"
    elif score >= 0.40:
        color, label = WARN, "MED"
    else:
        color, label = PRIMARY, "LOW"
    return f"""
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:90px;height:6px;background:#1E2D45;border-radius:3px;overflow:hidden;">
        <div style="width:{score_pct}%;height:100%;background:{color};border-radius:3px;"></div>
      </div>
      <span style="font-family:'Space Mono',monospace;font-size:0.8rem;color:{color};
                   min-width:32px;">{score_pct}</span>
      <span style="font-size:0.7rem;background:{color}22;color:{color};border:1px solid {color}55;
                   border-radius:4px;padding:2px 6px;font-family:'Space Mono',monospace;font-weight:700;">{label}</span>
    </div>"""


def upload_card(label: str, file_type: str, icon: str, accept: list):
    st.markdown(f"""
    <div class="animate-in" style="background:{BG_CARD};border:1px solid #1E2D45;
                border-radius:12px;padding:1.4rem;margin-bottom:0.8rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.8rem;">
        <span style="font-size:1.4rem;">{icon}</span>
        <span style="font-family:'Space Mono',monospace;font-size:0.9rem;font-weight:700;color:{TEXT_MAIN};">{label}</span>
        <span style="font-size:0.7rem;background:{PRIMARY}18;color:{PRIMARY};
                     border:1px solid {PRIMARY}44;border-radius:6px;padding:2px 8px;
                     font-family:'Space Mono',monospace;">{file_type}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    return st.file_uploader("", type=accept, key=f"upload_{file_type}", label_visibility="collapsed")


def callout(text: str, kind: str = "info"):
    colors = {"info": (PRIMARY, "ℹ"), "warn": (WARN, "⚠"), "error": (DANGER, "✕"), "success": (PRIMARY, "✓")}
    c, icon = colors.get(kind, colors["info"])
    st.markdown(f"""
    <div class="animate-in" style="background:{c}0F;border:1px solid {c}44;border-radius:10px;
                padding:1rem 1.2rem;display:flex;gap:12px;align-items:center;margin:0.8rem 0;">
      <div style="background:{c}22;color:{c};font-size:1.2rem;width:32px;height:32px;
                  border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
        {icon}
      </div>
      <span style="font-size:0.9rem;color:{TEXT_MAIN};line-height:1.5;">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def ai_explanation_card(test_name: str, root_cause: str, recommended_fix: str, confidence: str, score: float, severity: str):
    tier_colors = {"HIGH": DANGER, "MEDIUM": WARN, "LOW": PRIMARY, "UNKNOWN": TEXT_MUTED}
    tc = tier_colors.get(severity.upper(), PRIMARY)
    
    # Process confidence for progress bar (strip % if present)
    conf_str = str(confidence).replace('%', '').strip()
    try:
        conf_val = int(conf_str)
    except:
        conf_val = 0
    
    st.markdown(f"""
    <div class="animate-in" style="display:flex;gap:16px;margin:1.5rem 0 1rem;flex-wrap:wrap;">
      <div style="background:{tc}18;border:1px solid {tc}44;border-radius:10px;
                  padding:0.8rem 1.2rem;display:flex;align-items:center;gap:10px;">
        <span style="font-size:0.75rem;color:{tc};font-family:'Space Mono',monospace;">SEVERITY</span>
        <span style="font-family:'Space Mono',monospace;font-weight:700;font-size:1.1rem;color:{tc};">{severity.upper()}</span>
      </div>
      <div style="background:{BG_CARD};border:1px solid #1E2D45;border-radius:10px;
                  padding:0.8rem 1.2rem;display:flex;align-items:center;gap:10px;">
        <span style="font-size:0.75rem;color:{TEXT_MUTED};font-family:'Space Mono',monospace;">SCORE</span>
        <span style="font-family:'Space Mono',monospace;font-weight:700;font-size:1.1rem;color:{tc};">{score:.2f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="animate-in" style="background:{BG_CARD};border:1px solid #1E2D45;border-radius:16px;overflow:hidden;margin-bottom:2rem;box-shadow:0 8px 24px rgba(0,0,0,0.2);">
      <div style="background:#1A2438;padding:1rem 1.5rem;border-bottom:1px solid #1E2D45;
                  display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:12px;">
            <span style="color:{PRIMARY};font-size:1.2rem;">🔬</span>
            <span style="font-family:'Space Mono',monospace;font-size:1rem;font-weight:700;color:{TEXT_MAIN};">{test_name}</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px;background:{BG_DEEP};padding:6px 12px;border-radius:20px;border:1px solid #2A3550;">
            <span style="font-size:0.75rem;color:{TEXT_MUTED};font-family:'Space Mono',monospace;">CONFIDENCE</span>
            <div style="width:80px;height:6px;background:#1E2D45;border-radius:3px;overflow:hidden;">
                <div style="width:{conf_val}%;height:100%;background:{PRIMARY};border-radius:3px;"></div>
            </div>
            <span style="font-family:'Space Mono',monospace;font-weight:700;font-size:0.85rem;color:{PRIMARY};">{conf_val}%</span>
        </div>
      </div>
      
      <div style="padding:1.5rem;">
        <div style="background:{BG_DEEP};border:1px solid #2A3550;border-radius:12px;padding:1.2rem;margin-bottom:1.2rem;">
            <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:{DANGER};margin-bottom:0.6rem;display:flex;align-items:center;gap:6px;">
                <span>🎯</span> ROOT CAUSE
            </div>
            <div style="font-size:0.95rem;color:{TEXT_MAIN};line-height:1.6;white-space:pre-wrap;">{root_cause}</div>
        </div>
        
        <div style="background:{PRIMARY}0A;border:1px solid {PRIMARY}33;border-radius:12px;padding:1.2rem;">
            <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:{PRIMARY};margin-bottom:0.6rem;display:flex;align-items:center;gap:6px;">
                <span>🛠️</span> RECOMMENDED FIX
            </div>
            <div style="font-size:0.95rem;color:{TEXT_MAIN};line-height:1.6;white-space:pre-wrap;">{recommended_fix}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    st.markdown(f"""
    <div class="animate-in" style="text-align:center;padding:5rem 2rem;background:{BG_CARD};border:1px dashed #2A3550;border-radius:16px;margin:2rem 0;">
      <div style="font-size:3.5rem;margin-bottom:1.2rem;opacity:0.9;">{icon}</div>
      <h3 style="margin:0 0 0.8rem;font-family:'Space Mono',monospace;color:{TEXT_MAIN};font-size:1.3rem;">{title}</h3>
      <p style="color:{TEXT_MUTED};font-size:0.95rem;max-width:450px;margin:0 auto;line-height:1.5;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
