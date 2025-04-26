import streamlit as st
import exam_manager

def display_exam_management(teacher_id: str):
    # Load all exams associated with the teacher
    exams = exam_manager.load_exams(teacher_id)
    
    st.subheader("Manage Exams")
    
    # Get the previously selected exam from session state, default to "Exam History"
    default_exam = st.session_state.get("selected_exam_option", "Exam History")
    
    # Create a dropdown menu with "Exam History" and existing exams
    # The index calculation ensures the previously selected exam remains selected after page refresh
    exam_option = st.selectbox(
        "Select an Exam or Create New",
        ["Exam History"] + list(exams.values()),
        index=(["Exam History"] + list(exams.values())).index(default_exam)
        if default_exam in ["Exam History"] + list(exams.values())
        else 0
    )
    selected_exam_id = None
    
    # Handle exam selection and creation logic
    if exam_option != "Exam History":
        # If an existing exam is selected, find its ID from the exams dictionary
        selected_exam_id = [k for k, v in exams.items() if v == exam_option][0]
    else:
        # If "Exam History" is selected, show interface for creating a new exam
        new_exam_name = st.text_input("New Exam Name")
        if st.button("Create Exam"):
            if new_exam_name:
                # Create new exam and save it to the database
                exam_id = exam_manager.save_exam(teacher_id, new_exam_name)
                if exam_id:
                    # Show success message and update the UI
                    st.success(f"Exam '{new_exam_name}' created! ✅")
                    exams = exam_manager.load_exams(teacher_id)
                    # Store the new exam name in session state for persistence
                    st.session_state["selected_exam_option"] = new_exam_name
                    st.rerun()
            else:
                # Show error if exam name is empty
                st.error("Please enter an exam name! ⚠️")
    
    return selected_exam_id, exams