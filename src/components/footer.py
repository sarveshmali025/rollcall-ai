import streamlit as st
from src.ui.based_layout import get_tokens

def footer_home():
    st.markdown(f"""
            <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center;">
                <p style="font-weight:bold; color:white !important; margin:0;">created with &nbsp;&#10084;&nbsp; by &nbsp;Sarvesh</p>
            </div>
                """ , unsafe_allow_html=True)

def footer_dashboard():
    t = get_tokens()
    st.markdown(f"""
            <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center;">
                <p style="font-weight:bold; color:{t['text_muted']} !important; margin:0;">created with &nbsp;&#10084;&nbsp; by &nbsp;Sarvesh</p>
            </div>
                """ , unsafe_allow_html=True)
