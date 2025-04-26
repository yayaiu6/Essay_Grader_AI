import streamlit as st
import submission_manager
import utils
from streamlit_autorefresh import st_autorefresh

def display_submission_viewer(teacher_id: str, selected_exam_id: int, exams: dict):
    # Display the exam title as a subheader
    st.subheader(f"Submissions for {exams[selected_exam_id]}")
    
    # Auto-refresh the page every 10 seconds to check for new submissions
    st_autorefresh(interval=10 * 1000, key="submissions_refresh")
    
    # Manual refresh button for immediate updates
    if st.button("Refresh Submissions 🔄"):
        st.rerun()

    # Load all submissions for the selected exam and its questions
    submissions = submission_manager.load_submissions(teacher_id, selected_exam_id)
    questions = utils.load_questions(teacher_id, selected_exam_id)
    
    # Track the number of submissions to detect new ones
    if "last_submission_count" not in st.session_state:
        st.session_state["last_submission_count"] = len(submissions)
    
    # Show notification when new submissions are received
    if len(submissions) > st.session_state["last_submission_count"]:
        st.success("New submission received! ✅")
        st.session_state["last_submission_count"] = len(submissions)

    if submissions:
        # Iterate through each submission
        for idx, sub in enumerate(submissions):
            # Skip invalid submission entries
            if not isinstance(sub, dict):
                continue
            try:
                # Create expandable section for each submission with student info and score
                with st.expander(f"Student: {sub['student_name']} - Score: {sub['total_score']}/{sub['max_score']}"):
                    # Display submission header with styling
                    st.markdown(f"<h3 style='color: #4CAF50;'>Submission Details</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 16px;'><b>Total Score:</b> <span style='color: #2196F3;'>{sub['total_score']} / {sub['max_score']}</span></p>", unsafe_allow_html=True)
                    
                    # Create a bordered container for submission details
                    with st.container(border=True):
                        st.write(f"## {sub['student_name']}'s Submission")
                        st.markdown(f"<p style='font-weight: bold; font-size: 16px;'>Student Name: <span style='color:#009688;'>{sub['student_name']}</span></p>", unsafe_allow_html=True)
                        
                        # Display each question and its answer
                        for q_text, answer in sub['answers'].items():
                            st.write(f"\n**Question:** {q_text}")
                            # Handle different question types (Short Answer vs Multiple Choice)
                            if questions[q_text]['type'] == "Short Answer":
                                st.text_area("Answer:", value=answer if isinstance(answer, str) else ", ".join(answer), key=f"sub_{idx}_{q_text}", disabled=True)
                            else:
                                st.multiselect("Answer:", questions[q_text]['options'], default=answer if isinstance(answer, list) else [answer], key=f"sub_{idx}_{q_text}", disabled=True)
                            
                            # Display question score if evaluated
                            if q_text in sub['evaluations']:
                                eval_data = sub['evaluations'][q_text]
                                st.markdown(f"**Score:** <span style='color: #009688;'>{eval_data['score']}/10</span>", unsafe_allow_html=True)
            
            # Error handling for malformed submission data
            except KeyError:
                st.error(f"Error in submission data at index {idx}. Skipping this entry. ⚠️")
            except Exception as e:
                st.error(f"Failed to process submission: {str(e)} ⚠️")
    else:
        # Display message when no submissions are available
        st.write("No submissions yet.")