import streamlit as st
from src.ui.based_layout import theme_toggle_button, get_tokens

def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
            <div class="rc-home-brand">
                <img class="rc-brand-logo rc-brand-logo-home" src="{logo_url}" />
                <h1 class="rc-brand-title rc-brand-title-home">ROLL <br/>CALL AI</h1>
            </div>
                """ , unsafe_allow_html=True)
    
def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    t = get_tokens()
    st.markdown(f"""
            <div class="rc-dashboard-brand">
                <img class="rc-brand-logo rc-brand-logo-dashboard" src="{logo_url}" />
               <h2 class="rc-brand-title rc-brand-title-dashboard" style='color:{t["primary"]} !important;'>ROLL <br/>CALL AI</h2>
            </div>
                """ , unsafe_allow_html=True)


def toggle_with_action(action_label, key_suffix=None, **button_kwargs):
    """Renders the Sun/Moon theme toggle immediately to the LEFT of a single
    action button (Logout / Go back to home / etc). Returns True if the
    action button itself was clicked, exactly like a normal st.button call -
    callers just wrap their existing st.button(...) call with this."""
    suffix = key_suffix or button_kwargs.get('key', action_label)
    t_col, btn_col = st.columns([1, 4.2], vertical_alignment='center')
    with t_col:
        theme_toggle_button(key_suffix=suffix)
    with btn_col:
        return st.button(action_label, **button_kwargs)
