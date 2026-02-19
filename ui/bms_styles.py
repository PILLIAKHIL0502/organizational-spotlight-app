"""
Bristol Myers Squibb custom styles and components.
"""

import streamlit as st
from config.branding import BMS_COLORS, FONTS, LOGO_PATH, COMPANY_NAME, APP_TITLE


def load_custom_css():
    """Load custom CSS with BMS branding."""
    css = f"""
    <style>
        /* Import custom fonts */
        @font-face {{
            font-family: 'BMSRegular';
            src: url('assets/fonts/BMSRegular.ttf') format('truetype'),
                 url('assets/fonts/BMSRegular.otf') format('opentype'),
                 url('assets/fonts/BMSRegular.woff') format('woff'),
                 url('assets/fonts/BMSRegular.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }}

        @font-face {{
            font-family: 'BMSBold';
            src: url('assets/fonts/BMSBold.ttf') format('truetype'),
                 url('assets/fonts/BMSBold.otf') format('opentype'),
                 url('assets/fonts/BMSBold.woff') format('woff'),
                 url('assets/fonts/BMSBold.woff2') format('woff2');
            font-weight: bold;
            font-style: normal;
        }}

        /* Global font application */
        html, body, [class*="css"] {{
            font-family: {FONTS['regular']};
            color: {BMS_COLORS['text_primary']};
        }}

        /* Headers */
        h1, h2, h3, h4, h5, h6, .bms-heading {{
            font-family: {FONTS['heading']};
            color: {BMS_COLORS['text_primary']};
        }}

        /* Primary color accents */
        .stButton > button[kind="primary"] {{
            background-color: {BMS_COLORS['primary']};
            border-color: {BMS_COLORS['primary']};
            font-family: {FONTS['bold']};
        }}

        .stButton > button[kind="primary"]:hover {{
            background-color: {BMS_COLORS['primary_dark']};
            border-color: {BMS_COLORS['primary_dark']};
        }}

        /* Links and highlights */
        a, .stMarkdown a {{
            color: {BMS_COLORS['primary']};
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {BMS_COLORS['background_alt']};
        }}

        /* Input focus states */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {{
            border-color: {BMS_COLORS['primary']};
            box-shadow: 0 0 0 0.2rem rgba(190, 43, 187, 0.25);
        }}

        /* Success messages */
        .stSuccess {{
            background-color: rgba(0, 167, 88, 0.1);
            border-left: 4px solid {BMS_COLORS['success']};
        }}

        /* Info messages */
        .stInfo {{
            background-color: rgba(0, 102, 204, 0.1);
            border-left: 4px solid {BMS_COLORS['info']};
        }}

        /* Warning messages */
        .stWarning {{
            background-color: rgba(255, 107, 53, 0.1);
            border-left: 4px solid {BMS_COLORS['warning']};
        }}

        /* Error messages */
        .stError {{
            background-color: rgba(220, 20, 60, 0.1);
            border-left: 4px solid {BMS_COLORS['error']};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-family: {FONTS['bold']};
            color: {BMS_COLORS['text_secondary']};
        }}

        .stTabs [aria-selected="true"] {{
            color: {BMS_COLORS['primary']};
            border-bottom-color: {BMS_COLORS['primary']};
        }}

        /* Metrics */
        [data-testid="stMetricValue"] {{
            font-family: {FONTS['bold']};
            color: {BMS_COLORS['primary']};
        }}

        /* Expander */
        .streamlit-expanderHeader {{
            font-family: {FONTS['bold']};
            color: {BMS_COLORS['text_primary']};
        }}

        /* Custom BMS header */
        .bms-header {{
            background: linear-gradient(135deg, {BMS_COLORS['primary']} 0%, {BMS_COLORS['secondary']} 100%);
            padding: 20px;
            border-radius: 8px;
            color: white;
            margin-bottom: 30px;
        }}

        .bms-logo-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .bms-logo {{
            max-height: 60px;
            background: white;
            padding: 10px;
            border-radius: 8px;
        }}

        .bms-title {{
            font-family: {FONTS['bold']};
            font-size: 32px;
            margin: 0;
            color: white;
        }}

        .bms-subtitle {{
            font-family: {FONTS['regular']};
            font-size: 16px;
            margin: 5px 0 0 0;
            color: rgba(255, 255, 255, 0.9);
        }}

        /* Status badges */
        .bms-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-family: {FONTS['bold']};
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Cards */
        .bms-card {{
            background: white;
            border: 1px solid {BMS_COLORS['border']};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .bms-card:hover {{
            box-shadow: 0 4px 8px rgba(190, 43, 187, 0.1);
            border-color: {BMS_COLORS['primary']};
        }}

        /* Form labels */
        .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {{
            font-family: {FONTS['bold']};
            color: {BMS_COLORS['text_primary']};
        }}

        /* Remove emoji from elements */
        .no-emoji {{
            font-style: normal;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_bms_header(title: str = APP_TITLE, subtitle: str = None):
    """Render BMS branded header with logo."""
    try:
        # Try to use the logo
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(LOGO_PATH, width=200)
        with col2:
            st.markdown(f'<h1 style="font-family: {FONTS["heading"]}; color: {BMS_COLORS["primary"]}; margin-top: 20px;">{title}</h1>', unsafe_allow_html=True)
            if subtitle:
                st.markdown(f'<p style="font-family: {FONTS["regular"]}; color: {BMS_COLORS["text_secondary"]}; font-size: 16px;">{subtitle}</p>', unsafe_allow_html=True)
    except:
        # Fallback if logo not found
        st.markdown(f'<h1 style="font-family: {FONTS["heading"]}; color: {BMS_COLORS["primary"]};">{COMPANY_NAME}</h1>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="font-family: {FONTS["heading"]}; color: {BMS_COLORS["text_primary"]};">{title}</h2>', unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<p style="font-family: {FONTS["regular"]}; color: {BMS_COLORS["text_secondary"]};">{subtitle}</p>', unsafe_allow_html=True)

    st.markdown("---")


def render_bms_sidebar_header(user_name: str, user_role: str, user_email: str):
    """Render professional sidebar header."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f'<div style="font-family: {FONTS["bold"]}; font-size: 18px; color: {BMS_COLORS["text_primary"]};">{user_name}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f'<div style="font-family: {FONTS["regular"]}; font-size: 14px; color: {BMS_COLORS["text_secondary"]};">Role: {user_role.title()}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f'<div style="font-family: {FONTS["regular"]}; font-size: 12px; color: {BMS_COLORS["text_secondary"]};">{user_email}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")
