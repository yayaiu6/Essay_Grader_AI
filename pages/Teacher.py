import streamlit as st
import exam_management
import question_editor
import submission_viewer
import utils

# Check if user is authenticated, redirect to login if not
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Please login first! ⚠️")
    st.page_link("Home.py", label="Go to Login")
else:
    # Get teacher ID from session and display dashboard
    teacher_id = st.session_state["teacher_id"]
    st.title(f"Eshraq - {teacher_id}'s Dashboard")

    # Display exam management interface and get selected exam
    selected_exam_id, exams = exam_management.display_exam_management(teacher_id)
    
    if selected_exam_id:
        # Create three tabs for different exam management functions
        tab1, tab2, tab3 = st.tabs(["Add/Edit Questions", "Share Exam", "Manage Submissions"])

        # Tab 1: Question Editor Interface
        with tab1:
            question_editor.display_question_editor(teacher_id, selected_exam_id, exams)

        # Tab 2: Exam Sharing and Preview Interface
        with tab2:
            st.subheader(f"Share Exam Link for {exams[selected_exam_id]}")
            # Generate shareable link for students
            exam_link = utils.generate_exam_link(teacher_id, selected_exam_id)
            st.write("Share this link with your students:")
            st.code(exam_link)

            # Display exam preview section
            st.write("### Exam Preview")
            with st.container(border=True):
                st.write("## Eshraq - Exam")
                st.write("Sample Student Name: _____________")
                # Load and display all exam questions
                questions = utils.load_questions(teacher_id, selected_exam_id)
                for q_text, q_data in questions.items():
                    st.write(f"\n**Question:** {q_text}")
                    # Handle different question types (Short Answer or Multiple Choice)
                    if q_data['type'] == "Short Answer":
                        st.text_area("Answer:", key=f"preview_{q_text}", disabled=True)
                    else:
                        st.multiselect("Choose all that apply:", q_data['options'], key=f"preview_{q_text}", disabled=True)

        # Tab 3: Submission Management Interface
        with tab3:
            submission_viewer.display_submission_viewer(teacher_id, selected_exam_id, exams)
