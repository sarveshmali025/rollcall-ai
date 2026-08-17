import streamlit as st

# ---------------------------------------------------------------------------
# RollCall AI design tokens
# Brand stays anchored to the product's existing identity (Discord-style
# blurple/pink, chunky "Climate Crisis" display type for hero/brand text,
# 'Outfit' for body, 'JetBrains Mono' for data) - elevated, not replaced.
# ---------------------------------------------------------------------------

THEMES = {
    "dark": {
        "bg": "#0F1024",
        "bg_gradient": "radial-gradient(circle at 15% -10%, #23255C 0%, #0F1024 55%)",
        "surface": "#1C1E42",
        "surface_alt": "#23255C",
        "primary": "#5865F2",
        "primary_hover": "#4752C4",
        "secondary": "#EB459E",
        "text": "#F5F6FF",
        "text_muted": "#A5A9D6",
        "border": "rgba(255,255,255,0.08)",
        "border_strong": "#34366B",
        "success": "#3BD671",
        "success_bg": "rgba(59,214,113,0.14)",
        "warning": "#FFB020",
        "warning_bg": "rgba(255,176,32,0.14)",
        "danger": "#F1434A",
        "danger_bg": "rgba(241,67,74,0.14)",
        "shadow": "0 24px 48px -16px rgba(0,0,0,0.65)",
        "shadow_sm": "0 8px 20px -10px rgba(0,0,0,0.55)",
        "input_bg": "#23255C",
        "scrollbar": "#34366B",
        "row_hover": "rgba(88,101,242,0.10)",
    },
    "light": {
        "bg": "#F6F7FF",
        "bg_gradient": "radial-gradient(circle at 15% -10%, #ECEDFF 0%, #FAFAFF 55%)",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F2FF",
        "primary": "#5865F2",
        "primary_hover": "#4752C4",
        "secondary": "#EB459E",
        "text": "#1B1C33",
        "text_muted": "#5B5E82",
        "border": "rgba(27,28,51,0.08)",
        "border_strong": "#E3E5FB",
        "success": "#1B8F4C",
        "success_bg": "rgba(27,143,76,0.10)",
        "warning": "#A9600A",
        "warning_bg": "rgba(169,96,10,0.10)",
        "danger": "#C21F2C",
        "danger_bg": "rgba(194,31,44,0.10)",
        "shadow": "0 24px 48px -20px rgba(88,101,242,0.28)",
        "shadow_sm": "0 8px 20px -12px rgba(88,101,242,0.20)",
        "input_bg": "#FFFFFF",
        "scrollbar": "#E3E5FB",
        "row_hover": "rgba(88,101,242,0.06)",
    },
}


def get_theme_name():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    return st.session_state.theme


def get_tokens():
    return THEMES[get_theme_name()]


def theme_toggle_button(key_suffix=""):
    """Compact icon-only Sun/Moon toggle - no text label."""
    theme = get_theme_name()
    icon = ":material/light_mode:" if theme == "dark" else ":material/dark_mode:"
    if st.button("", icon=icon, key=f"theme_toggle_{key_suffix}", type="tertiary", help="Switch appearance"):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()


def style_background_home():
    # Home always shows the app's dark/navy visual background (matching the
    # in-app dark theme look) regardless of the toggle, so the white
    # tagline/feature pills always stay readable. The toggle still sets the
    # theme preference that applies once the user enters Student/Teacher.
    dark = THEMES["dark"]
    st.markdown(
        f"""
        <style>
            .stApp{{
                background: {dark['bg_gradient']} !important;
                background-color: {dark['bg']} !important;
            }}

            /* Home background is intentionally dark/navy.
               Only the two portal columns become cards; header/action columns
               must remain normal transparent layout containers. */
            .block-container{{
                max-width: 1120px !important;
                padding-top: 1.1rem !important;
                padding-bottom: 2.2rem !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_background_dashboard():
    t = get_tokens()
    st.markdown(
        f"""
        <style>
            .stApp{{
                background: {t['bg_gradient']} !important;
                background-color: {t['bg']} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_base_layout():
    t = get_tokens()

    st.markdown(
        f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&family=Outfit:wght@100..900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {{
            --rc-bg: {t['bg']};
            --rc-surface: {t['surface']};
            --rc-surface-alt: {t['surface_alt']};
            --rc-primary: {t['primary']};
            --rc-primary-hover: {t['primary_hover']};
            --rc-secondary: {t['secondary']};
            --rc-text: {t['text']};
            --rc-text-muted: {t['text_muted']};
            --rc-border: {t['border']};
            --rc-border-strong: {t['border_strong']};
            --rc-success: {t['success']};
            --rc-success-bg: {t['success_bg']};
            --rc-warning: {t['warning']};
            --rc-warning-bg: {t['warning_bg']};
            --rc-danger: {t['danger']};
            --rc-danger-bg: {t['danger_bg']};
            --rc-shadow: {t['shadow']};
            --rc-shadow-sm: {t['shadow_sm']};
            --rc-input-bg: {t['input_bg']};
            --rc-row-hover: {t['row_hover']};
            --rc-scrollbar: {t['scrollbar']};
        }}

        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.001ms !important;
                transition-duration: 0.001ms !important;
            }}
        }}

        /* =========================================================
           STREAMLIT CHROME REMOVAL
           ========================================================= */
        [data-testid="stHeader"] {{ display: none; }}
        [data-testid="stToolbar"] {{ display: none; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        [data-testid="stDecoration"] {{ display: none; }}

        .block-container {{
            padding-top: 1.6rem !important;
            padding-bottom: 3rem !important;
            max-width: 1180px;
        }}

        /* =========================================================
           BASE TYPE + COLOR
           Font-family and color are set ONCE at the app root and at
           Streamlit's own content containers (never on bare span/div),
           then simply INHERIT down the DOM. Any element that sets its
           OWN explicit color (status chips, brand headers on fixed
           backgrounds) keeps that color automatically - inheritance
           never outranks an element's own declaration, so there is no
           specificity fight and nothing needs guesswork !important
           chains scattered everywhere.
           ========================================================= */
        .stApp {{
            font-family: 'Outfit', sans-serif;
            color: var(--rc-text);
        }}

        [data-testid="stMarkdownContainer"],
        [data-testid="stHeading"],
        [data-testid="stWidgetLabel"],
        [data-testid="stCaptionContainer"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {{
            color: var(--rc-text) !important;
        }}

        [data-testid="stCaptionContainer"] {{
            color: var(--rc-text-muted) !important;
        }}

        /* Material icon glyphs need their own icon font regardless of
           the Outfit inheritance above, or the icon name renders as
           literal text instead of a glyph. */
        [data-testid="stIconMaterial"] {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
        }}

        /* =========================================================
           HEADINGS
           No color set here beyond a safe inherited baseline - the
           rule above already colors their container. This keeps
           inline-styled headers (home screen cards, brand title)
           free to keep their own intentional color.
           ========================================================= */
        h1 {{
            font-family: 'Climate Crisis', sans-serif;
            font-weight: 400;
            font-size: 3.4rem;
            line-height: 1.02;
            letter-spacing: 0.5px;
            margin-bottom: 0.2rem;
            color: var(--rc-text);
        }}

        h2 {{
            font-family: 'Climate Crisis', sans-serif;
            font-weight: 400;
            font-size: 2rem;
            line-height: 1.08;
            margin-bottom: 0.5rem;
            color: var(--rc-text);
        }}

        h3 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--rc-text);
        }}

        h4 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            color: var(--rc-text);
        }}

        /* Decorative underline accent under page-level h1 titles for a
           stronger, more finished brand moment. */
        h1::after {{
            content: "";
            display: block;
            width: 500px;
            height: 5px;
            margin-top: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--rc-primary), var(--rc-secondary));
        }}

        .rc-mono {{
            font-family: 'JetBrains Mono', monospace !important;
        }}

       .rc-role-title {{
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            opacity: 1 !important;
            font-weight: 800 !important;
            text-align: center !important;
            visibility: visible !important;
            filter: none !important;
            mix-blend-mode: normal !important;
        }}

        /* =========================================================
           BUTTONS
           ========================================================= */
        button {{
            border-radius: 1.1rem !important;
            background-color: var(--rc-primary) !important;
            color: white !important;
            padding: 9px 20px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: transform 0.16s ease, box-shadow 0.16s ease, background-color 0.16s ease, filter 0.16s ease !important;
            box-shadow: var(--rc-shadow-sm);
        }}

        button[kind="secondary"],
        [data-testid^="stBaseButton-secondary"] {{
            background-color: var(--rc-secondary) !important;
        }}

        button[kind="tertiary"],
        [data-testid^="stBaseButton-tertiary"] {{
            background-color: var(--rc-surface-alt) !important;
            color: var(--rc-text) !important;
            border: 1px solid var(--rc-border-strong) !important;
            box-shadow: none !important;
        }}

        button:hover {{
            transform: translateY(-2px);
            filter: brightness(1.06);
            box-shadow: var(--rc-shadow);
        }}

        button:active {{
            transform: translateY(0) scale(0.97);
        }}

        button:focus-visible {{
            outline: 2px solid var(--rc-secondary) !important;
            outline-offset: 2px;
        }}

        button p, button span:not([data-testid="stIconMaterial"]) {{
            color: inherit !important;
        }}

        /* Compact circular treatment for icon-only buttons (theme toggle) */
        button:has([data-testid="stIconMaterial"]):not(:has(p)) {{
            padding: 9px 12px !important;
            aspect-ratio: 1 / 1;
        }}

        /* =========================================================
           INPUTS / SELECTS / TEXTAREAS
           ========================================================= */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input {{
            background-color: var(--rc-input-bg) !important;
            color: var(--rc-text) !important;
            border: 1.5px solid var(--rc-border-strong) !important;
            border-radius: 0.85rem !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }}

        [data-testid="stTextInput"] input:hover,
        [data-testid="stTextArea"] textarea:hover,
        [data-testid="stNumberInput"] input:hover,
        [data-baseweb="select"] > div:hover {{
            border-color: rgba(88,101,242,0.55) !important;
        }}

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {{
            border-color: var(--rc-primary) !important;
            box-shadow: 0 0 0 3px rgba(88,101,242,0.22) !important;
        }}

        [data-baseweb="popover"] {{
            font-family: 'Outfit', sans-serif !important;
        }}

        /* Select-box dropdown option list (BaseWeb renders this in a
           portal, so it does NOT automatically inherit .stApp styling -
           needs its own explicit theme-aware background/text/hover). */
        [data-baseweb="popover"] [role="listbox"],
        [data-baseweb="menu"] {{
            background-color: var(--rc-surface) !important;
            color: var(--rc-text) !important;
            border: 1px solid var(--rc-border-strong) !important;
            border-radius: 0.8rem !important;
        }}

        [data-baseweb="menu"] li {{
            color: var(--rc-text) !important;
        }}

        [data-baseweb="menu"] li:hover,
        [data-baseweb="menu"] [aria-selected="true"] {{
            background-color: var(--rc-row-hover) !important;
        }}

        /* Tooltip popover shown for st.button/st.text_input `help=` */
        [data-testid="stTooltipContent"] {{
            background-color: var(--rc-surface) !important;
            color: var(--rc-text) !important;
            border: 1px solid var(--rc-border-strong) !important;
            border-radius: 0.6rem !important;
        }}

        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {{
            color: var(--rc-text-muted) !important;
            opacity: 1 !important;
        }}

        /* =========================================================
           EXPANDERS / FORMS / BORDERED CONTAINERS
           ========================================================= */
        [data-testid="stExpander"] {{
            background-color: var(--rc-surface) !important;
            border: 1px solid var(--rc-border-strong) !important;
            border-radius: 1.1rem !important;
            box-shadow: var(--rc-shadow-sm);
            overflow: hidden;
        }}

        [data-testid="stForm"] {{
            background-color: var(--rc-surface-alt) !important;
            border: 1px dashed var(--rc-border-strong) !important;
            border-radius: 1.1rem !important;
            padding: 1.2rem !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 1.2rem !important;
        }}

        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: var(--rc-surface);
            border: 1px solid var(--rc-border-strong);
            box-shadow: var(--rc-shadow-sm);
            padding: 0.4rem 0.2rem;
        }}

        /* =========================================================
           DATAFRAMES (native st.dataframe - kept for anything not
           migrated to the custom rc-table below)
           ========================================================= */
        [data-testid="stDataFrame"] {{
            border-radius: 1rem !important;
            overflow: hidden;
            border: 1px solid var(--rc-border-strong) !important;
        }}

        /* =========================================================
           CUSTOM PREMIUM TABLE (replaces st.dataframe in Records /
           Analytics so text color is 100% guaranteed correct in both
           themes - Streamlit's native dataframe grid is canvas-drawn
           and does not reliably follow custom CSS theming).
           ========================================================= */
        .rc-table-wrap {{
            border: 1px solid var(--rc-border-strong);
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: var(--rc-shadow-sm);
            margin-bottom: 0.6rem;
        }}

        .rc-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.92rem;
        }}

        .rc-table thead th {{
            background: var(--rc-surface-alt);
            color: var(--rc-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 0.72rem;
            font-weight: 700;
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid var(--rc-border-strong);
        }}

        .rc-table tbody td {{
            padding: 11px 16px;
            color: var(--rc-text);
            background: var(--rc-surface);
            border-bottom: 1px solid var(--rc-border);
        }}

        .rc-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        .rc-table tbody tr {{
            transition: background-color 0.15s ease;
        }}

        .rc-table tbody tr:hover td {{
            background: var(--rc-row-hover);
        }}

        /* =========================================================
           ALERTS / DIVIDER / DIALOG / SCROLLBAR
           ========================================================= */
        [data-testid="stAlert"] {{
            border-radius: 1rem !important;
            font-weight: 500;
        }}

        /* Keep Streamlit alerts/toasts readable in BOTH themes.
           Do not let the app-wide text color turn alert text invisible. */
        [data-testid="stAlert"] {{
            background-color: var(--rc-surface-alt) !important;
            color: var(--rc-text) !important;
            border: 1px solid var(--rc-border-strong) !important;
        }}

        [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span {{
            color: var(--rc-text) !important;
        }}

        [data-testid="stToast"] {{
            background-color: var(--rc-surface) !important;
            color: var(--rc-text) !important;
            border: 1px solid var(--rc-border-strong) !important;
        }}

        [data-testid="stToast"] [data-testid="stMarkdownContainer"],
        [data-testid="stToast"] p,
        [data-testid="stToast"] span {{
            color: var(--rc-text) !important;
        }}

        hr {{
            border-color: var(--rc-border-strong) !important;
            opacity: 0.6;
        }}

        [data-testid="stDialog"] > div {{
            background-color: var(--rc-surface) !important;
            color: var(--rc-text) !important;
            border-radius: 1.4rem !important;
            border: 1px solid var(--rc-border-strong) !important;
        }}

        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--rc-scrollbar); border-radius: 8px; }}

        /* =========================================================
           REUSABLE SURFACES
           ========================================================= */
        .rc-card {{
            background: var(--rc-surface);
            border: 1px solid var(--rc-border-strong);
            border-radius: 1.4rem;
            box-shadow: var(--rc-shadow-sm);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            color: var(--rc-text);
        }}

        .rc-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--rc-shadow);
        }}

        /* ---------- Status chip (signature element) ---------- */
        .rc-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            font-family: 'Outfit', sans-serif;
            white-space: nowrap;
        }}

        .rc-chip .rc-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .rc-chip-present {{ background: var(--rc-success-bg); color: var(--rc-success) !important; }}
        .rc-chip-present .rc-dot {{
            background: var(--rc-success);
            animation: rc-pulse 1.8s ease-in-out infinite;
        }}

        .rc-chip-absent {{ background: var(--rc-danger-bg); color: var(--rc-danger) !important; }}
        .rc-chip-absent .rc-dot {{ background: var(--rc-danger); }}

        .rc-chip-warning {{ background: var(--rc-warning-bg); color: var(--rc-warning) !important; }}
        .rc-chip-warning .rc-dot {{ background: var(--rc-warning); }}

        @keyframes rc-pulse {{
            0%   {{ box-shadow: 0 0 0 0 rgba(59,214,113,0.5); }}
            70%  {{ box-shadow: 0 0 0 6px rgba(59,214,113,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(59,214,113,0); }}
        }}

        /* ---------- Stat card grid (analytics) ---------- */
        .rc-stat-card {{
            background: var(--rc-surface);
            border: 1px solid var(--rc-border-strong);
            border-radius: 1.2rem;
            padding: 1.15rem 1.3rem;
            box-shadow: var(--rc-shadow-sm);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        .rc-stat-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--rc-primary), var(--rc-secondary));
            opacity: 0.85;
        }}
        .rc-stat-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--rc-shadow);
        }}
        .rc-stat-label {{
            font-size: 0.76rem;
            font-weight: 700;
            color: var(--rc-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
        }}
        .rc-stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.1rem;
            font-weight: 700;
            color: var(--rc-text);
            line-height: 1;
        }}
        .rc-stat-sub {{
            font-size: 0.78rem;
            color: var(--rc-text-muted);
            margin-top: 0.35rem;
        }}

        /* ---------- Insight card ---------- */
        .rc-insight {{
            background: var(--rc-surface-alt);
            border-left: 4px solid var(--rc-secondary);
            border-radius: 0.8rem;
            padding: 0.85rem 1.05rem;
            margin-bottom: 0.6rem;
            font-size: 0.92rem;
            color: var(--rc-text);
        }}

        /* ---------- Section label above groups of content ---------- */
        .rc-eyebrow {{
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--rc-secondary);
            margin-bottom: 0.2rem;
        }}

        /* ---------- Brand/header polish ---------- */
        .rc-home-brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 1rem auto 1.4rem;
            text-align: center;
        }}

        .rc-brand-logo {{
            object-fit: contain;
            display: block;
            transition: transform 0.28s ease, filter 0.28s ease;
        }}

        .rc-brand-logo-home {{ width: 100px; height: 100px; }}
        .rc-brand-logo-dashboard {{ width: 85px; height: 85px; }}

        .rc-home-brand:hover .rc-brand-logo,
        .rc-dashboard-brand:hover .rc-brand-logo {{
            transform: translateY(-2px) scale(1.025);
            filter: drop-shadow(0 8px 12px rgba(88,101,242,0.22));
        }}

        .rc-brand-title {{
            margin: 0 !important;
            font-family: 'Climate Crisis', sans-serif !important;
            font-weight: 400 !important;
            line-height: 1.02 !important;
        }}

        .rc-brand-title-home {{
            color: #F5F6FF !important;
            -webkit-text-fill-color: #F5F6FF !important;
            text-align: center !important;
            font-size: 3.35rem !important;
        }}

        .rc-dashboard-brand {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
        }}

        .rc-brand-title-dashboard {{
            text-align: left !important;
            font-size: 2rem !important;
        }}

        /* Keep theme/action controls compact and visually balanced. */
        button[data-testid*="theme_toggle"] {{
            min-width: 44px !important;
            width: 44px !important;
            height: 44px !important;
            padding: 8px !important;
            border-radius: 50% !important;
        }}

        /* =========================================================
           HOME PAGE POLISH
           Moderate motion only: no full-page animation/flicker.
           ========================================================= */
        .rc-tagline {{
            text-align: center;
            font-size: 1.02rem;
            font-weight: 500;
            color: rgba(255,255,255,0.90) !important;
            max-width: 600px;
            margin: 0 auto 1.35rem auto;
            line-height: 1.55;
            letter-spacing: 0.01em;
        }}

        .rc-feature-row {{
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }}

        .rc-feature-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 15px;
            border-radius: 999px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.28);
            color: #FFFFFF !important;
            font-size: 0.82rem;
            font-weight: 600;
            backdrop-filter: blur(8px);
            box-shadow: 0 5px 18px rgba(0,0,0,0.10);
            transition: transform 0.22s ease, background-color 0.22s ease,
                        border-color 0.22s ease, box-shadow 0.22s ease;
        }}

        .rc-feature-pill:hover {{
            transform: translateY(-2px);
            background: rgba(255,255,255,0.18);
            border-color: rgba(255,255,255,0.42);
            box-shadow: 0 8px 22px rgba(0,0,0,0.16);
        }}

        /* Only the two home portal columns become cards. This fixes the
           previous giant white header/action boxes caused by styling every
           Streamlit column globally. */
        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon) {{
            box-sizing: border-box;
            background: rgba(250,250,255,0.985) !important;
            padding: 2rem 2rem 1.45rem !important;
            border-radius: 2rem !important;
            border: 1px solid rgba(255,255,255,0.78) !important;
            box-shadow: 0 24px 55px -18px rgba(7,10,45,0.48) !important;
            text-align: center;
            position: relative;
            overflow: hidden;
            transform: translateY(0);
            transition: transform 0.28s ease, box-shadow 0.28s ease,
                        border-color 0.28s ease;
            animation: rc-home-rise 0.55s ease both;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon):nth-child(2) {{
            animation-delay: 0.08s;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon)::before {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: radial-gradient(circle at 50% -20%, rgba(88,101,242,0.14), transparent 42%);
            opacity: 0.9;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon):hover {{
            transform: translateY(-6px);
            box-shadow: 0 32px 65px -20px rgba(7,10,45,0.58) !important;
            border-color: rgba(88,101,242,0.28) !important;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon) [data-testid="stImage"] {{
            display: flex;
            justify-content: center;
            margin: 0.15rem auto 0.75rem auto;
            position: relative;
            z-index: 1;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon) [data-testid="stImage"] img {{
            transition: transform 0.28s ease, filter 0.28s ease;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon):hover [data-testid="stImage"] img {{
            transform: translateY(-4px) scale(1.025);
            filter: drop-shadow(0 8px 10px rgba(88,101,242,0.16));
        }}

        .rc-portal-icon {{
            width: 58px;
            height: 58px;
            border-radius: 17px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.55rem;
            margin: 0 auto 0.8rem auto;
            background: linear-gradient(135deg, var(--rc-primary), var(--rc-secondary));
            box-shadow: 0 10px 24px -8px rgba(88,101,242,0.55);
            position: relative;
            z-index: 1;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon):hover .rc-portal-icon {{
            transform: translateY(-3px) rotate(-2deg);
            box-shadow: 0 14px 30px -8px rgba(88,101,242,0.68);
        }}

        /* Role labels intentionally stay dark and bold on the fixed-light
           portal cards in BOTH app themes. */
        h2.rc-role-title {{
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            opacity: 1 !important;
            visibility: visible !important;
            filter: none !important;
            mix-blend-mode: normal !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
            font-size: 1.7rem !important;
            line-height: 1.15 !important;
            text-align: center !important;
            margin: 0.25rem 0 0.7rem !important;
            position: relative;
            z-index: 2;
        }}

        h2.rc-role-title::after {{
            content: "";
            display: block;
            width: 180px;
            height: 4px;
            margin: 8px auto 0;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--rc-primary), var(--rc-secondary));
            opacity: 0.85;
        }}

        .rc-portal-desc {{
            color: #4B5278 !important;
            font-size: 0.92rem;
            font-weight: 500;
            text-align: center;
            margin: 4px auto 16px;
            line-height: 1.5;
            max-width: 440px;
            position: relative;
            z-index: 2;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon) button {{
            position: relative;
            z-index: 2;
            margin-top: 0.15rem !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease,
                        filter 0.22s ease !important;
        }}

        .stApp div[data-testid="stColumn"]:has(.rc-portal-icon) button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 14px 26px -10px rgba(88,101,242,0.65) !important;
        }}

        @keyframes rc-home-rise {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Subtle ambient glow; slow enough to feel like depth, not a gimmick. */
        .stApp::before {{
            content: "";
            position: fixed;
            width: 420px;
            height: 420px;
            left: -180px;
            top: 18%;
            border-radius: 50%;
            background: rgba(88,101,242,0.075);
            filter: blur(80px);
            pointer-events: none;
            z-index: 0;
        }}

        @keyframes rc-ambient {{
            from {{ transform: translate3d(0,0,0); opacity: 0.55; }}
            to   {{ transform: translate3d(90px,25px,0); opacity: 0.9; }}
        }}

        /* ---------- Navigation pill bar (dashboard tabs) ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(button[kind="primary"]):has(button[kind="tertiary"]) {{
            background: var(--rc-surface-alt) !important;
            border-radius: 1.4rem !important;
            box-shadow: none !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )
