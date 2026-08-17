import streamlit as st

def status_chip_html(status, label=None):
    """
    status: 'present' | 'absent' | 'warning'
    Returns raw HTML string (caller wraps in st.markdown(..., unsafe_allow_html=True))
    so it can be embedded inline inside larger markdown blocks or table cells.
    Colors are set directly on the element itself (not inherited), so they
    render correctly regardless of theme.
    """
    variants = {
        'present': ('rc-chip-present', '\u2713', label or 'Present'),
        'absent': ('rc-chip-absent', '\u2715', label or 'Absent'),
        'warning': ('rc-chip-warning', '\u26A0', label or 'Needs Review'),
    }
    css_class, symbol, text = variants.get(status, variants['absent'])
    return (
        f'<span class="rc-chip {css_class}">'
        f'<span class="rc-dot"></span>{symbol} {text}'
        f'</span>'
    )


def status_chip(status, label=None):
    st.markdown(status_chip_html(status, label), unsafe_allow_html=True)
