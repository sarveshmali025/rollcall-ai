import streamlit as st
import textwrap
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.based_layout import (
    style_background_dashboard,
    style_background_home,
    style_base_layout
)


def home_screen():

    # Existing UI/theme setup
    style_background_home()
    style_base_layout()

    # Header
    header_home()

    # Tagline + feature pills
    st.html("""
<div class="rc-home-intro">
    <p class="rc-tagline">
        AI-powered attendance for modern classrooms &mdash; face, voice and
        multimodal verification, built to feel effortless.
    </p>

    <div class="rc-feature-row">
        <span class="rc-feature-pill">&#128272; Face Recognition</span>
        <span class="rc-feature-pill">&#127908; Voice Verification</span>
        <span class="rc-feature-pill">&#10024; Multimodal AI</span>
        <span class="rc-feature-pill">&#128202; Live Analytics</span>
    </div>
</div>
""")

    # Student + Teacher portals
    col1, col2 = st.columns(2, gap="large")

    # =========================================================
    # STUDENT PORTAL
    # =========================================================
    with col1:

        st.markdown(
            """
            <div class="rc-portal-icon">&#127891;</div>

            <h2 class="rc-role-title">
                I'm Student
            </h2>

            <p class="rc-portal-desc">
                Mark your attendance instantly with a quick face scan
                &mdash; no passwords needed.
            </p>
            """,
            unsafe_allow_html=True
        )

        # Center mascot
        student_img_col = st.columns([1, 1, 1])[1]

        with student_img_col:
            st.image(
                "https://i.ibb.co/844D9Lrt/mascot-student.png",
                width=120
            )

        # Student portal button
        if st.button(
            "Student Portal",
            type="primary",
            icon=":material/arrow_outward:",
            icon_position="right",
            width="stretch"
        ):
            st.session_state["login_type"] = "student"
            st.rerun()

    # =========================================================
    # TEACHER PORTAL
    # =========================================================
    with col2:

        st.markdown(
            """
            <div class="rc-portal-icon">&#128104;&#8205;&#127979;</div>

            <h2 class="rc-role-title">
                I'm Teacher
            </h2>

            <p class="rc-portal-desc">
                Create classes, run AI-verified attendance and track
                analytics in real time.
            </p>
            """,
            unsafe_allow_html=True
        )

        # Center mascot
        teacher_img_col = st.columns([1, 1, 1])[1]

        with teacher_img_col:
            st.image(
                "https://i.ibb.co/CsmQQV6X/mascot-teacher.png",
                width=145
            )

        # Teacher portal button
        if st.button(
            "Teacher Portal",
            type="primary",
            icon=":material/arrow_outward:",
            icon_position="right",
            width="stretch"
        ):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # Footer
    footer_home()