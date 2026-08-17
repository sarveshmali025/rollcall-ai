import html
import streamlit as st


def render_html_table(headers, rows):
    """
    headers: list of column header strings (plain text, auto-escaped)
    rows: list of rows, each a list of cell values. Each cell value is
          either a plain string/number (auto-escaped) or a dict
          {'html': '<raw trusted html>'} for cells that need to embed
          something like a status chip.
    """
    parts = ['<div class="rc-table-wrap"><table class="rc-table">']

    parts.append('<thead><tr>')
    for h in headers:
        parts.append(f'<th>{html.escape(str(h))}</th>')
    parts.append('</tr></thead>')

    parts.append('<tbody>')
    for row in rows:
        parts.append('<tr>')
        for cell in row:
            if isinstance(cell, dict) and 'html' in cell:
                parts.append(f'<td>{cell["html"]}</td>')
            else:
                parts.append(f'<td>{html.escape(str(cell))}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table></div>')

    st.markdown(''.join(parts), unsafe_allow_html=True)
