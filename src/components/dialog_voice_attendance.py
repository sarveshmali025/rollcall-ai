import streamlit as st
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result
from src.pipelines.voice_pipeline import process_bulk_audio
import pandas as pd
from datetime import datetime


@st.dialog("Voice Attendance")
def voice_attendance_dialog(subject_id):
    st.write('Record classroom audio. Each student can say a short phrase (e.g. "I am present, my name is Akash").')

    audio_data = st.audio_input('Record classroom audio')

    if audio_data and st.button('Run Voice Analysis', type='primary', width='stretch'):
        with st.spinner('Analyzing voices...'):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No students enrolled in this course')
                return

            candidates_dict = {}
            student_map = {}

            for node in enrolled_students:
                student = node['students']
                student_map[student['student_id']] = student
                if student.get('voice_embedding'):
                    candidates_dict[student['student_id']] = student['voice_embedding']

            identified = process_bulk_audio(audio_data.read(), candidates_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for student_id, student in student_map.items():
                is_present = student_id in identified

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Source": f"Voice match ({identified[student_id]:.2f})" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student_id,
                    'subject_id': subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

        show_attendance_result(pd.DataFrame(results), attendance_to_log)
