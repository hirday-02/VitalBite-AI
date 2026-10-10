"""
VitalBite AI — Light Premium Healthcare Design System & Custom CSS Engine
Implements clean, polished healthcare SaaS aesthetic with crisp cyan/sky radiance,
rounded cards, dark navy legibility, professional typography, and inline SVG metric helpers.
"""
import streamlit as st

def inject_custom_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
    }

    /* Ambient Light Canvas Background */
    .stApp {
        background: linear-gradient(145deg, #F8FAFC 0%, #F0F9FF 40%, #E0F2FE 75%, #F8FAFC 100%) !important;
        background-attachment: fixed !important;
        color: #0F172A !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1240px !important;
    }

    /* Top Brand Header Bar */
    .vitalbite-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 1.4rem;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px -2px rgba(14, 165, 233, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .vitalbite-logo-box {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .vitalbite-emblem {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.25);
    }
    .vitalbite-brand-name {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.025em;
    }
    .vitalbite-chip-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .vitalbite-chip-beta {
        background: rgba(14, 165, 233, 0.1);
        color: #0284C7;
        border: 1px solid rgba(14, 165, 233, 0.25);
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .vitalbite-chip-assistant {
        background: rgba(13, 148, 136, 0.1);
        color: #0D9488;
        border: 1px solid rgba(13, 148, 136, 0.25);
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .vitalbite-user-pill {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(226, 232, 240, 0.9);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        color: #1E293B;
        font-size: 0.84rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.45rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* Clean Rounded Cards */
    .med-card {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px -2px rgba(14, 165, 233, 0.05), 0 1px 3px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .med-card:hover {
        border-color: rgba(186, 230, 253, 0.9);
        box-shadow: 0 8px 24px -4px rgba(14, 165, 233, 0.09);
        transform: translateY(-1px);
    }
    .med-card-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.65rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        letter-spacing: -0.015em;
    }
    .med-card-subtitle {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748B;
        margin-bottom: 0.35rem;
    }

    /* Selectable Goal Cards */
    .goal-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1.5px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .goal-card-active {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(2, 132, 199, 0.06) 100%);
        border: 1.5px solid #0284C7;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12);
    }

    /* Food Category Container */
    .food-category-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.03);
    }

    /* Meal Card Styling */
    .meal-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.04);
        transition: all 0.2s ease;
    }
    .meal-card:hover {
        border-color: #0EA5E9;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.08);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 1.1rem !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.22) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.32) !important;
    }

    /* Secondary / Download Buttons */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1.5px solid rgba(226, 232, 240, 0.9) !important;
        color: #0284C7 !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(14, 165, 233, 0.06) !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(240, 249, 255, 0.95) !important;
        border-color: #0284C7 !important;
        color: #0369A1 !important;
        transform: translateY(-1px) !important;
    }

    /* Sidebar Navigation Customization */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
        box-shadow: 2px 0 16px rgba(14, 165, 233, 0.03) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem !important;
    }

    /* Form Controls & Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 12px !important;
        color: #0F172A !important;
        font-weight: 500 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #0284C7 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
    }

    /* Polished Error Notice Card */
    .error-card {
        background: rgba(254, 242, 242, 0.95) !important;
        border: 1px solid rgba(252, 165, 165, 0.8) !important;
        border-radius: 14px !important;
        padding: 0.95rem 1.25rem !important;
        color: #991B1B !important;
        margin-bottom: 0.85rem !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.06) !important;
    }
    .error-card-title {
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        color: #DC2626 !important;
        margin-bottom: 0.3rem !important;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Emergency Alert Box */
    .emergency-overlay {
        background: linear-gradient(135deg, rgba(254, 242, 242, 0.95) 0%, rgba(254, 226, 226, 0.9) 100%);
        border: 2px solid #EF4444;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.12);
    }
    .emergency-btn {
        display: inline-block;
        background: #DC2626;
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 0.95rem;
        padding: 0.7rem 1.4rem;
        border-radius: 12px;
        text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.3);
        transition: all 0.2s ease;
    }
    .emergency-btn:hover {
        background: #B91C1C;
        transform: translateY(-1px);
    }

    /* Medical Disclaimer Banner */
    .disclaimer-box {
        background: rgba(240, 253, 250, 0.9);
        border-left: 4px solid #0D9488;
        padding: 0.85rem 1.15rem;
        border-radius: 0 12px 12px 0;
        font-size: 0.82rem;
        color: #334155;
        line-height: 1.5;
        margin-top: 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 6px rgba(13, 148, 136, 0.04);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent !important;}
    </style>
    """
    st.html(css)

def render_bmi_gauge_html(bmi_val: float, category: str, color: str) -> str:
    """Generates a clean inline SVG semi-circular arc gauge for Body Mass Index."""
    clamped = max(15.0, min(35.0, bmi_val))
    pct = (clamped - 15.0) / 20.0
    dash_offset = 125.6 * (1 - pct)

    return f"""<div style="display: flex; align-items: center; justify-content: space-between;"><div><div style="font-size: 2.1rem; font-weight: 800; color: {color}; line-height: 1.1; letter-spacing: -0.02em;">{bmi_val}</div><div style="font-size: 0.84rem; color: #475569; font-weight: 600; margin-top: 0.25rem;">{category}</div></div><div style="text-align: center;"><svg width="84" height="48" viewBox="0 0 100 60"><path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="rgba(14,165,233,0.12)" stroke-width="10" stroke-linecap="round" /><path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round" stroke-dasharray="125.6" stroke-dashoffset="{dash_offset}" /><text x="50" y="46" text-anchor="middle" fill="#0F172A" font-size="13" font-weight="800">{bmi_val}</text></svg></div></div>"""

def render_completeness_donut_html(percentage: int, completed: int, total: int) -> str:
    """Generates a clean inline SVG circular progress donut for profile completeness."""
    pct = max(0, min(100, percentage))
    dash_offset = 201.0 * (1 - (pct / 100.0))

    return f"""<div style="display: flex; align-items: center; justify-content: space-between;"><div><div style="font-size: 2.1rem; font-weight: 800; color: #0284C7; line-height: 1.1; letter-spacing: -0.02em;">{pct}%</div><div style="font-size: 0.84rem; color: #475569; font-weight: 600; margin-top: 0.25rem;">{completed}/{total} Fields Completed</div></div><div style="text-align: center;"><svg width="56" height="56" viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(14,165,233,0.12)" stroke-width="8" /><circle cx="40" cy="40" r="32" fill="none" stroke="#0284C7" stroke-width="8" stroke-dasharray="201.0" stroke-dashoffset="{dash_offset}" stroke-linecap="round" transform="rotate(-90 40 40)" /><text x="40" y="46" text-anchor="middle" fill="#0F172A" font-size="14" font-weight="800">{pct}%</text></svg></div></div>"""

def render_macro_progress_bar_html(label: str, actual: float, target: float, unit: str = "g", color: str = "#0EA5E9") -> str:
    """Generates a clean visual progress bar for daily target achievement."""
    pct = round((actual / max(1.0, target)) * 100) if target > 0 else 0
    clamped_pct = min(120, max(0, pct))
    bar_width = min(100, clamped_pct)
    badge_bg = "rgba(13, 148, 136, 0.12)" if pct >= 90 else "rgba(217, 119, 6, 0.12)"
    badge_color = "#0D9488" if pct >= 90 else "#D97706"

    return f"""
    <div style="margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.84rem; margin-bottom: 0.3rem;">
            <span style="font-weight: 700; color: #1E293B;">{label}</span>
            <div style="display: flex; align-items: center; gap: 0.45rem;">
                <span style="color: #64748B; font-size: 0.8rem; font-weight: 500;">{actual} / {target} {unit}</span>
                <span style="background: {badge_bg}; color: {badge_color}; font-weight: 800; font-size: 0.74rem; padding: 0.12rem 0.5rem; border-radius: 6px;">{pct}%</span>
            </div>
        </div>
        <div style="width: 100%; height: 8px; background: rgba(14, 165, 233, 0.12); border-radius: 6px; overflow: hidden;">
            <div style="width: {bar_width}%; height: 100%; background: {color}; border-radius: 6px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """
