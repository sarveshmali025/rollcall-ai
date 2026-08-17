import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
from src.components.data_table import render_html_table
from src.components.status_badge import status_chip_html
import time


from src.database.db import create_attendance

def _classify_status_text(text):
    if text.startswith('✅') or ('Present' in text and 'Needs Review' not in text and 'Flagged' not in text):
        return 'present'
    if text.startswith('⚠️') or 'Needs Review' in text or 'Flagged' in text:
        return 'warning'
    return 'absent'

def show_attendance_result(df, logs):
    st.write('Please review attendance before confirming.')

    headers = list(df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in headers:
            text = str(row[col])
            if any(text.startswith(m) for m in ('✅', '❌', '⚠️')):
                status = _classify_status_text(text)
                clean_label = text.split(' ', 1)[1] if ' ' in text else text
                cells.append({'html': status_chip_html(status, clean_label)})
            else:
                cells.append(text)
        rows.append(cells)

    render_html_table(headers, rows)

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', width='stretch'):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('Confirm & Save', width='stretch', type='primary'):
            try:
                create_attendance(logs)
                st.toast("Attendance taken")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error('Sync failed!')



@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)

