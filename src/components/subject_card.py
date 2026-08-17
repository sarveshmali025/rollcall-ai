import streamlit as st
from src.ui.based_layout import get_tokens

def subject_card(name, code, section, stats=None, footer_callback=None):
    t = get_tokens()

    html = f"""
        <div class="rc-card" style="padding:1.6rem; border-left: 6px solid {t['secondary']}; margin-bottom:1.2rem;">
        <h3 style="margin:0; color: {t['text']}; font-size: 1.4rem;">{name}</h3>
        <p style="color:{t['text_muted']} !important; margin:8px 0 12px 0;">
            Code : <span style="background:{t['surface_alt']}; color:{t['primary']}; padding:2px 10px; border-radius:8px; font-family:'JetBrains Mono', monospace; font-size:0.85rem;">{code}</span>
            &nbsp;|&nbsp; Section : {section}
        </p>
        """

    if stats:
        html += '<div style="display:flex; gap:8px; flex-wrap:wrap;">'
        for icon, label, value in stats:
            html += (
                f'<div style="background:{t["surface_alt"]}; color:{t["text"]}; '
                f'padding:6px 14px; border-radius:12px; font-size:0.9rem;">'
                f'{icon} <b class="rc-mono">{value}</b> {label}</div>'
            )
        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
