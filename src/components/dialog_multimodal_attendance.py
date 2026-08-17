import streamlit as st
from src.database.config import supabase
from src.components.data_table import render_html_table
from src.components.status_badge import status_chip_html
from src.database.db import create_attendance
from src.pipelines.face_pipeline import get_face_verification_scores
from src.pipelines.multimodal_pipeline import verify_multimodal
import numpy as np
import pandas as pd
from datetime import datetime


@st.dialog("Face + Voice Multimodal Verification")
def multimodal_attendance_dialog(subject_id):
    # Keep the verification result in session state because clicking any
    # Streamlit button reruns the script. Without this, attendance_to_log was
    # recreated as an empty/local variable and was lost before Save ran.
    state_key = f"multimodal_result_{subject_id}"
    result_state = st.session_state.get(state_key)

    if result_state is None:
        st.write(
            'Uses the classroom photos already added (via "Add Photos") together with a fresh '
            'audio recording. A student is marked present only if BOTH face and voice checks pass '
            'independently — a single matching modality is flagged for your manual review instead.'
        )

        if not st.session_state.get('attendance_images'):
            st.warning('Please add at least one classroom photo first using "Add Photos".')
            return

        audio_data = st.audio_input('Record classroom audio for voice verification')

        if audio_data and st.button('Run Multimodal Verification', type='primary', width='stretch', key=f'multimodal_run_{subject_id}'):
            with st.spinner('Cross-verifying face and voice...'):
                enrolled_res = (
                    supabase.table('subject_students')
                    .select("*, students(*)")
                    .eq('subject_id', subject_id)
                    .execute()
                )
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                    return

                student_map = {}
                candidates_voice_dict = {}

                for node in enrolled_students:
                    student = node['students']
                    student_map[student['student_id']] = student
                    if student.get('voice_embedding'):
                        candidates_voice_dict[student['student_id']] = student['voice_embedding']

                # Aggregate face scores across all captured photos; keep each
                # student's best (lowest-distance) match across photos.
                combined_face_scores = {}
                for img in st.session_state.attendance_images:
                    img_np = np.array(img.convert('RGB'))
                    scores = get_face_verification_scores(img_np)
                    for sid, dist in scores.items():
                        if sid not in combined_face_scores or dist < combined_face_scores[sid]:
                            combined_face_scores[sid] = dist

                report = verify_multimodal(
                    combined_face_scores,
                    audio_data.read(),
                    candidates_voice_dict,
                )

                report_rows = []
                attendance_to_log = []
                current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                for student_id, student in student_map.items():
                    entry = report.get(student_id, {
                        'face_score': None,
                        'face_match': False,
                        'voice_score': None,
                        'voice_match': False,
                        'decision': 'Absent',
                        'is_present': False,
                    })

                    face_result = (
                        f"Match ({entry['face_score']:.2f})" if entry['face_match']
                        else (
                            f"No match ({entry['face_score']:.2f})"
                            if entry['face_score'] is not None else "Not detected"
                        )
                    )
                    voice_result = (
                        f"Match ({entry['voice_score']:.2f})" if entry['voice_match']
                        else (
                            f"No match ({entry['voice_score']:.2f})"
                            if entry['voice_score'] is not None else "Not detected"
                        )
                    )

                    if entry['face_match'] and entry['voice_match']:
                        decision_label = "✅ Present (Verified)"
                    elif entry['face_match'] or entry['voice_match']:
                        decision_label = "⚠️ Needs Review (1 modality only)"
                    else:
                        decision_label = "❌ Absent"

                    report_rows.append({
                        "Name": student['name'],
                        "ID": student_id,
                        "Face Result": face_result,
                        "Voice Result": voice_result,
                        "Final Decision": decision_label,
                    })

                    attendance_to_log.append({
                        'student_id': student_id,
                        'subject_id': subject_id,
                        'timestamp': current_timestamp,
                        'is_present': bool(entry['is_present']),
                    })

                # Persist the result across the rerun caused by clicking Save.
                st.session_state[state_key] = {
                    'report_rows': report_rows,
                    'attendance_to_log': attendance_to_log,
                }
                st.rerun()

        return

    # ---------- Verification result / save stage ----------
    st.subheader('AI Verification Report')
    st.caption(
        'Students flagged "Needs Review" are currently logged as absent. '
        'You can correct them later from Attendance Records.'
    )

    report_rows = result_state['report_rows']
    attendance_to_log = result_state['attendance_to_log']

    df = pd.DataFrame(report_rows)
    headers = list(df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for column in headers:
            text = str(row[column])
            if column == 'Final Decision':
                if text.startswith('✅'):
                    cells.append({'html': status_chip_html('present', text[2:].strip())})
                elif text.startswith('⚠️'):
                    cells.append({'html': status_chip_html('warning', text[2:].strip())})
                else:
                    cells.append({'html': status_chip_html('absent', text[2:].strip())})
            else:
                cells.append(text)
        rows.append(cells)
    render_html_table(headers, rows)

    save_col, discard_col = st.columns(2)

    with discard_col:
        if st.button('Discard', width='stretch', key=f'multimodal_discard_{subject_id}'):
            st.session_state.pop(state_key, None)
            st.session_state.attendance_images = []
            st.rerun()

    with save_col:
        if st.button(
            'Confirm & Save Attendance',
            width='stretch',
            type='primary',
            key=f'multimodal_save_{subject_id}',
        ):
            try:
                create_attendance(attendance_to_log)
                st.session_state.pop(state_key, None)
                st.session_state.attendance_images = []
                st.toast('Multimodal attendance saved successfully')
                st.rerun()
            except Exception as e:
                st.error(f'Attendance could not be saved: {e}')