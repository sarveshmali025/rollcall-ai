import streamlit as st
from src.ui.based_layout import style_background_dashboard , style_base_layout
from src.components.header import header_dashboard, toggle_with_action 
from src.components.footer import footer_home , footer_dashboard
from src.database.db import (
    check_teacher_exists , create_teacher , teacher_login , get_teacher_subjects ,
    get_subject_attendance_logs , update_attendance_log , get_correction_audit_trail ,
    get_teacher_attendance_logs, delete_subject
)
from src.components.dialog__create_subject import create_subject_dialog 
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photos import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.dialog_multimodal_attendance import multimodal_attendance_dialog
from src.components.status_badge import status_chip_html
from src.components.data_table import render_html_table
from src.pipelines.face_pipeline import predict_attendance
from src.analytics.attendance_analytics import (
    overall_stats, subject_wise_stats, student_wise_stats,
    trend_over_time, low_attendance_students, generate_smart_insights
)
from src.utils.export_utils import build_excel_bytes, build_pdf_bytes
import numpy as np
import pandas as pd
from src.database.config import supabase
from datetime import datetime


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
        return

    if "teacher_login_type" not in st.session_state:
        st.session_state.teacher_login_type = "login"

    if st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    else:
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome , {teacher_data['name']}""")
        if toggle_with_action("Logout", type="secondary", key="loginbackbtm", shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()
        st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    with st.container(border=True):
        tab1, tab2, tab3, tab4 = st.columns(4)

        with tab1:
            type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
            if st.button('Take Attendance', type=type1, width='stretch', icon=':material/ar_on_you:'):
                st.session_state.current_teacher_tab = 'take_attendance'
                st.rerun()

        with tab2:
            type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
            if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
                st.session_state.current_teacher_tab = 'manage_subjects'
                st.rerun()

        with tab3:
            type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
            if st.button('Attendance Records', type=type3, width='stretch', icon=':material/cards_stack:'):
                st.session_state.current_teacher_tab = 'attendance_records'
                st.rerun()

        with tab4:
            type4 = "primary" if st.session_state.current_teacher_tab == 'analytics' else "tertiary"
            if st.button('Analytics', type=type4, width='stretch', icon=':material/monitoring:'):
                st.session_state.current_teacher_tab = 'analytics'
                st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
    elif st.session_state.current_teacher_tab == "analytics":
        teacher_tab_analytics()

    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
            st.warning('You havent created any subjects yet! Please create one to begin!')
            return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)

    with c4:
        if st.button('AI Verified (Face+Voice)', type='primary', width='stretch', icon=':material/verified_user:', disabled=not has_photos):
            multimodal_attendance_dialog(selected_subject_id)

@st.dialog("Delete Subject")
def delete_subject_dialog(subject_id, subject_name, teacher_id):
    st.warning(f"This will permanently delete {subject_name} and its attendance history, enrollments, and correction records.")
    st.write("This action cannot be undone.")

    confirm = st.checkbox("I understand that this subject and its records will be deleted.", key=f"confirm_delete_{subject_id}")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", width="stretch", type="tertiary"):
            st.rerun()

    with col2:
        if st.button("Delete Permanently", width="stretch", type="primary", disabled=not confirm):
            try:
                delete_subject(subject_id, teacher_id)
                st.session_state.pop(f"delete_subject_{subject_id}", None)
                st.toast(f"{subject_name} deleted successfully")
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete subject: {e}")


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')
    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            def subject_actions(sub=sub):
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button(
                        f"Share Code: {sub['name']}",
                        key=f"share_{sub['subject_code']}",
                        icon=":material/share:",
                        width="stretch",
                    ):
                        share_subject_dialog(sub['name'], sub['subject_code'])
                with action_col2:
                    if st.button(
                        "Delete Subject",
                        key=f"delete_subject_btn_{sub['subject_id']}",
                        icon=":material/delete_forever:",
                        type="tertiary",
                        width="stretch",
                    ):
                        delete_subject_dialog(sub['subject_id'], sub['name'], teacher_id)

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=subject_actions
            )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")

def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Attendance Records')

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.info('No subjects yet. Create one under Manage Subjects.')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
    selected_label = st.selectbox('Select Subject', options=list(subject_options.keys()), key='records_subject_select')
    selected_subject_id = subject_options[selected_label]
    selected_subject_name = selected_label.split(' - ')[0]

    export_c1, export_c2, export_c3 = st.columns([2, 1, 1])
    with export_c1:
        st.caption('Export this subject\'s full attendance history.')
    with export_c2:
        if st.button('Export Excel', width='stretch', icon=':material/download:', key='export_xlsx_btn'):
            export_logs = get_subject_attendance_logs(selected_subject_id)
            if not export_logs:
                st.warning('No records to export yet.')
            else:
                st.session_state['_export_xlsx_bytes'] = build_excel_bytes(selected_subject_name, export_logs)
    with export_c3:
        if st.button('Export PDF', width='stretch', icon=':material/picture_as_pdf:', key='export_pdf_btn'):
            export_logs = get_subject_attendance_logs(selected_subject_id)
            if not export_logs:
                st.warning('No records to export yet.')
            else:
                st.session_state['_export_pdf_bytes'] = build_pdf_bytes(selected_subject_name, export_logs)

    if st.session_state.get('_export_xlsx_bytes'):
        st.download_button(
            'Download Excel file', data=st.session_state['_export_xlsx_bytes'],
            file_name=f"{selected_subject_name}_attendance.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            width='stretch', key='dl_xlsx_btn'
        )
    if st.session_state.get('_export_pdf_bytes'):
        st.download_button(
            'Download PDF file', data=st.session_state['_export_pdf_bytes'],
            file_name=f"{selected_subject_name}_attendance.pdf",
            mime='application/pdf',
            width='stretch', key='dl_pdf_btn'
        )

    st.divider()

    if 'records_view' not in st.session_state:
        st.session_state.records_view = 'sessions'

    view_c1, view_c2 = st.columns(2)
    with view_c1:
        t1 = 'primary' if st.session_state.records_view == 'sessions' else 'tertiary'
        if st.button('Session Records', type=t1, width='stretch', key='records_view_sessions'):
            st.session_state.records_view = 'sessions'
            st.rerun()
    with view_c2:
        t2 = 'primary' if st.session_state.records_view == 'audit' else 'tertiary'
        if st.button('Correction Audit Trail', type=t2, width='stretch', key='records_view_audit'):
            st.session_state.records_view = 'audit'
            st.rerun()

    st.divider()

    if st.session_state.records_view == 'sessions':
        logs = get_subject_attendance_logs(selected_subject_id)

        if not logs:
            st.info('No attendance taken yet for this subject.')
            return

        sessions = {}
        for log in logs:
            sessions.setdefault(log['timestamp'], []).append(log)

        for ts in sorted(sessions.keys(), reverse=True):
            session_logs = sessions[ts]
            present_count = sum(1 for l in session_logs if l.get('is_present'))

            with st.expander(f"📅 {ts}  —  {present_count}/{len(session_logs)} present"):
                for log in session_logs:
                    log_id = log.get('id')
                    student_info = log.get('students') or {}
                    name = student_info.get('name', f"Student {log.get('student_id')}")

                    row_c1, row_c2, row_c3 = st.columns([2, 2, 1])
                    with row_c1:
                        st.write(name)
                    with row_c2:
                        st.markdown(status_chip_html('present' if log.get('is_present') else 'absent'), unsafe_allow_html=True)
                    with row_c3:
                        if st.button('Correct', key=f'correct_btn_{log_id}', width='stretch'):
                            st.session_state[f'editing_{log_id}'] = not st.session_state.get(f'editing_{log_id}', False)
                            st.rerun()

                    if st.session_state.get(f'editing_{log_id}'):
                        with st.form(key=f'correction_form_{log_id}'):
                            new_status = st.selectbox(
                                'New status', ['Present', 'Absent'],
                                index=0 if log.get('is_present') else 1,
                                key=f'status_select_{log_id}'
                            )
                            reason = st.text_input(
                                'Reason for correction', key=f'reason_input_{log_id}',
                                placeholder='e.g. AI misdetection, student was late'
                            )
                            submitted = st.form_submit_button('Save Correction')

                            if submitted:
                                if not reason:
                                    st.warning('Please provide a reason for the correction.')
                                else:
                                    try:
                                        update_attendance_log(
                                            log_id=log_id,
                                            new_is_present=(new_status == 'Present'),
                                            corrected_by=teacher_id,
                                            reason=reason
                                        )
                                        st.session_state[f'editing_{log_id}'] = False
                                        st.toast('Correction saved')
                                        st.rerun()
                                    except Exception as e:
                                        st.error('Failed to save correction. See remaining issues note for required database setup.')
                    st.divider()

    else:
        audit_trail = get_correction_audit_trail(selected_subject_id)

        if not audit_trail:
            st.info('No corrections have been made yet for this subject.')
        else:
            rows = []
            for entry in audit_trail:
                student_info = entry.get('students') or {}
                rows.append([
                    student_info.get('name', f"Student {entry.get('student_id')}"),
                    {'html': status_chip_html('present' if entry.get('original_status') else 'absent')},
                    {'html': status_chip_html('present' if entry.get('new_status') else 'absent')},
                    entry.get('reason') or '-',
                    entry.get('corrected_at'),
                ])
            render_html_table(['Student', 'Original', 'Corrected To', 'Reason', 'Corrected At'], rows)

def _stat_card(label, value, sub=None):
    sub_html = f'<div class="rc-stat-sub">{sub}</div>' if sub else ''
    st.markdown(
        f"""
        <div class="rc-stat-card">
            <div class="rc-stat-label">{label}</div>
            <div class="rc-stat-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def _pct_chip_html(pct):
    if pct >= 75:
        return status_chip_html('present', f'{pct}%')
    elif pct >= 50:
        return status_chip_html('warning', f'{pct}%')
    else:
        return status_chip_html('absent', f'{pct}%')

def teacher_tab_analytics():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Attendance Analytics')

    with st.spinner('Crunching attendance data...'):
        logs = get_teacher_attendance_logs(teacher_id)

    if not logs:
        st.info('No attendance data yet. Take attendance in at least one subject to see analytics.')
        return

    stats = overall_stats(logs)
    subj_df = subject_wise_stats(logs)

    st.subheader('Overview')
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _stat_card('Subjects', stats['total_subjects'])
    with k2:
        _stat_card('Students Tracked', stats['total_students'])
    with k3:
        _stat_card('Sessions Taken', stats['total_sessions'])
    with k4:
        _stat_card('Overall Attendance', f"{stats['overall_attendance_pct']}%")

    st.space()

    st.subheader('Smart Insights')
    all_student_df = student_wise_stats(logs)
    insights = generate_smart_insights(logs, subj_df, all_student_df)
    for insight in insights:
        st.markdown(f'<div class="rc-insight">{insight}</div>', unsafe_allow_html=True)

    st.space()
    st.divider()

    st.subheader('Subject-wise Attendance')
    if not subj_df.empty:
        with st.container(border=True):
            chart_df = subj_df.set_index('subject_name')[['attendance_pct']].rename(columns={'attendance_pct': 'Attendance %'})
            st.bar_chart(chart_df, width='stretch')

            rows = []
            for _, r in subj_df.iterrows():
                rows.append([
                    r['subject_name'], int(r['sessions']),
                    {'html': _pct_chip_html(r['attendance_pct'])},
                    int(r['records']),
                ])
            render_html_table(['Subject', 'Sessions', 'Attendance %', 'Total Records'], rows)

    st.divider()

    st.subheader('Student-wise Attendance')
    subjects = get_teacher_subjects(teacher_id)
    subject_options = {'All Subjects': None}
    subject_options.update({f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects})
    selected_label = st.selectbox('Filter by subject', options=list(subject_options.keys()), key='analytics_subject_filter')
    selected_subject_id = subject_options[selected_label]

    student_df = student_wise_stats(logs, subject_id=selected_subject_id)

    if student_df.empty:
        st.info('No records for this filter.')
    else:
        with st.container(border=True):
            rows = []
            for _, r in student_df.iterrows():
                rows.append([
                    r['student_name'], int(r['sessions']), int(r['attended']),
                    {'html': _pct_chip_html(r['attendance_pct'])},
                ])
            render_html_table(['Student', 'Sessions', 'Attended', 'Attendance %'], rows)

        low_df = low_attendance_students(student_df, threshold=75.0)
        if not low_df.empty:
            st.markdown(status_chip_html('warning', f'{len(low_df)} student(s) below 75% attendance'), unsafe_allow_html=True)
            with st.container(border=True):
                low_rows = [[r['student_name'], {'html': _pct_chip_html(r['attendance_pct'])}] for _, r in low_df.iterrows()]
                render_html_table(['Student', 'Attendance %'], low_rows)

    st.divider()

    st.subheader('Attendance Trend')
    trend_df = trend_over_time(logs, subject_id=selected_subject_id)
    if not trend_df.empty:
        with st.container(border=True):
            trend_chart_df = trend_df.set_index('date')[['attendance_pct']].rename(columns={'attendance_pct': 'Attendance %'})
            st.line_chart(trend_chart_df, width='stretch')
    else:
        st.info('Not enough dated sessions yet to show a trend.')

def login_teacher(username , password):
     if not username or not password:
          return False

     teacher = teacher_login(username , password)

     if teacher:
          st.session_state.user_role = 'teacher'
          st.session_state.teacher_data = teacher
          st.session_state.is_logged_in = True
          return True
     return False
def teacher_screen_login(): 
    c1 , c2 = st.columns(2,vertical_alignment='center' , gap = 'xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if toggle_with_action("Go back to home" , type = "secondary", key = "loginbackbtm" , shortcut="control+backspace" ):
                st.session_state['login_type'] = None
                st.rerun()    

    st.divider()

    left_pad, center, right_pad = st.columns([1, 1.4, 1])
    with center:
        with st.container(border=True):
            st.header('Login using password' , text_alignment='center')
            st.space()

            teacher_username = st.text_input("Enter username" , placeholder="Ananya roy")

            teacher_pass = st.text_input("Enter password" , type="password" , placeholder="Enter password")

            st.divider()

            btnc1 , btnc2 = st.columns(2)

            with btnc1:
                if st.button('Login' ,icon=':material/passkey:', shortcut="control+enter" , width="stretch"):
                    if login_teacher(teacher_username , teacher_pass):
                          st.toast("Welcome back !" , icon="🎉")
                          import time
                          time.sleep(1)
                          st.rerun()
                    else:
                        st.error("Inavlid username and password combination")

            with btnc2:
                if st.button('Register Instead' , icon=':material/passkey:' , type='primary' , width='stretch'):
                     st.session_state.teacher_login_type = 'register'
                     st.rerun()


    footer_dashboard()

def register_teacher(teacher_username , teacher_name , teacher_pass , teacher_pass_confirm):
     if not teacher_username or not teacher_pass:
          return False , "All fields are required !"
     if check_teacher_exists(teacher_username):
          return False, "Username already taken"
     if teacher_pass != teacher_pass_confirm:
          return False , "Password doesn't match"

     try:
        create_teacher( teacher_username , teacher_pass , teacher_name)
        return True, "Successfully Created ! Login Now"
     except Exception as e:
        return False , "Unexpected Error !"

def teacher_screen_register():
    c1 , c2 = st.columns(2,vertical_alignment='center' , gap = 'xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if toggle_with_action("Go back to home" , type = "secondary", key = "loginbackbtm" , shortcut="control+backspace" ):
                st.session_state['login_type'] = None
                st.rerun()
                
    st.divider()

    left_pad, center, right_pad = st.columns([1, 1.4, 1])
    with center:
        with st.container(border=True):
            st.header('Register your teacher profile', text_alignment='center')
            st.space()

            teacher_username = st.text_input("Enter username" , placeholder="ananyaroy")

            teacher_name = st.text_input("Enter name" , placeholder="Ananya roy")

            teacher_pass = st.text_input("Enter password" , type="password" , placeholder="Enter password")

            teacher_pass_confirm = st.text_input("Confirm your password" , type="password" , placeholder="Enter password")

            st.divider()

            btnc1 , btnc2 = st.columns(2)

            with btnc1:
                    if st.button('Register Now' ,icon=':material/passkey:', shortcut="control+enter" , width="stretch"):
                        success , message = register_teacher(teacher_username , teacher_name , teacher_pass , teacher_pass_confirm)
                        if success:
                              st.success(message)
                              import time
                              time.sleep(2)
                              st.session_state.teacher_login_type = "login"
                              st.rerun()
                        else:
                         st.error(message)
            with btnc2:
                    if st.button('Login Instead' , icon=':material/passkey:' , type='primary' , width='stretch'):
                         st.session_state.teacher_login_type = 'login'
                         st.rerun()
    footer_dashboard()