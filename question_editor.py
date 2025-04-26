import streamlit as st
import utils

def display_question_editor(teacher_id: str, selected_exam_id: int, exams: dict):
    # Load existing questions for the selected exam
    questions = utils.load_questions(teacher_id, selected_exam_id)
    
    # Section 1: Add New Question Interface
    st.subheader(f"Add New Question to {exams[selected_exam_id]}")
    
    # Basic question input fields
    new_question_text = st.text_input("New Question:")
    new_topic = st.text_input("Question Number:")
    new_question_type = st.selectbox("New Question Type:", ["Short Answer", "Multiple Choice"])
    
    # Dynamic form based on question type
    if new_question_type == "Short Answer":
        new_reference = st.text_area("Reference Answer:")
    else:
        # For multiple choice: collect options and correct answers
        new_options_text = st.text_area("Options (one per line):")
        options_list = [opt.strip() for opt in new_options_text.split("\n") if opt.strip()]
        new_correct_options = st.multiselect("Correct Options (select all that apply):", options_list)
    
    # Handle adding new question
    if st.button("Add New Question"):
        if new_question_text and new_topic:
            # Refresh questions data and prepare new question structure
            questions = utils.load_questions(teacher_id, selected_exam_id)
            new_question_data = {"type": new_question_type, "Question Number": new_topic}
            
            # Handle Short Answer type
            if new_question_type == "Short Answer":
                if new_reference:
                    new_question_data["reference"] = new_reference
                else:
                    st.error("Reference answer is required for Short Answer! ⚠️")
                    new_question_data = None
                    
            # Handle Multiple Choice type
            elif new_question_type == "Multiple Choice":
                # Process and validate options
                options = [opt.strip() for opt in new_options_text.split("\n") if opt.strip()]
                seen = set()
                # Remove duplicate options while preserving order
                unique_options = [opt for opt in options if not (opt in seen or seen.add(opt))]
                
                # Validate options and correct answers
                if not unique_options:
                    st.error("Please provide at least one option! ⚠️")
                    new_question_data = None
                elif not new_correct_options:
                    st.error("Please specify at least one correct option! ⚠️")
                    new_question_data = None
                else:
                    # Verify correct options exist in options list
                    invalid_correct = [opt for opt in new_correct_options if opt not in unique_options]
                    if invalid_correct:
                        st.error(f"Correct options {invalid_correct} are not in the list! ⚠️")
                        new_question_data = None
                    else:
                        new_question_data["options"] = unique_options
                        new_question_data["correct"] = new_correct_options
            
            # Save the new question if validation passed
            if new_question_data:
                if new_question_text in questions:
                    st.error("Question already exists! ⚠️")
                else:
                    questions[new_question_text] = new_question_data
                    if utils.save_questions(teacher_id, selected_exam_id, questions):
                        st.success("New question added! ✅")
                        st.rerun()
                    else:
                        st.error("Failed to save question! ⚠️")
        else:
            st.error("Question and Question Number are required! ⚠️")

    st.subheader("Existing Questions")
    if questions:
        for q_text, q_data in questions.items():
            with st.expander(f"Question: {q_text}"):
                st.write(f"Type: {q_data['type']}")
                st.write(f"Question Number: {q_data['Question Number']}")
                if q_data['type'] == "Short Answer":
                    st.write(f"Reference Answer: {q_data['reference']}")
                else:
                    st.write("Options:")
                    for opt in q_data.get('options', []):
                        st.write(f"- {opt}")
                    st.write(f"Correct Answers: {', '.join(q_data['correct']) if q_data['correct'] else 'None'}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Edit 📝", key=f"edit_{q_text}"):
                        st.session_state['editing_question'] = q_text
                with col2:
                    if st.button(f"Delete ❌", key=f"delete_{q_text}"):
                        current_questions = utils.load_questions(teacher_id, selected_exam_id)
                        if q_text in current_questions:
                            del current_questions[q_text]
                            if utils.save_questions(teacher_id, selected_exam_id, current_questions):
                                st.success("Question deleted successfully! ✅")
                                st.session_state['questions'] = current_questions
                                st.rerun()
                            else:
                                st.error("Failed to delete question! ⚠️")
                        else:
                            st.error("Question not found! ⚠️")

                if st.session_state.get('editing_question') == q_text:
                    st.write("### Edit Question")
                    edit_question_text = st.text_input("Question:", value=q_text, key=f"edit_q_{q_text}")
                    edit_topic = st.text_input("Question Number:", value=q_data['Question Number'], key=f"edit_Question Number_{q_text}")
                    if q_data['type'] == "Short Answer":
                        edit_reference = st.text_area("Reference Answer:", value=q_data['reference'], key=f"edit_ref_{q_text}")
                    else:
                        edit_options_text = st.text_area("Options (one per line):", value="\n".join(q_data['options']), key=f"edit_opt_{q_text}")
                        options_list = [opt.strip() for opt in edit_options_text.split("\n") if opt.strip()]
                        edit_correct_options = st.multiselect(
                            "Correct Options (select all that apply):", 
                            options_list, 
                            default=q_data['correct'], 
                            key=f"edit_corr_{q_text}"
                        )
                    
                    if st.button("Save Changes", key=f"save_{q_text}"):
                        if edit_question_text and edit_topic:
                            if q_data['type'] == "Short Answer" and edit_reference:
                                questions.pop(q_text)
                                questions[edit_question_text] = {
                                    "type": "Short Answer", 
                                    "Question Number": edit_topic, 
                                    "reference": edit_reference
                                }
                                utils.save_questions(teacher_id, selected_exam_id, questions)
                                st.success("Question updated! ✅")
                                st.session_state.pop('editing_question')
                                st.rerun()
                            elif q_data['type'] == "Multiple Choice":
                                new_options = [opt.strip() for opt in edit_options_text.split("\n") if opt.strip()]
                                seen = set()
                                unique_new_options = [opt for opt in new_options if not (opt in seen or seen.add(opt))]
                                if not unique_new_options:
                                    st.error("Please provide at least one option! ⚠️")
                                elif not edit_correct_options:
                                    st.error("Please specify at least one correct option! ⚠️")
                                else:
                                    invalid_correct = [opt for opt in edit_correct_options if opt not in unique_new_options]
                                    if invalid_correct:
                                        st.error(f"Correct options {invalid_correct} are not in the list! ⚠️")
                                    else:
                                        questions.pop(q_text)
                                        questions[edit_question_text] = {
                                            "type": "Multiple Choice",
                                            "Question Number": edit_topic,
                                            "options": unique_new_options,
                                            "correct": edit_correct_options
                                        }
                                        utils.save_questions(teacher_id, selected_exam_id, questions)
                                        st.success("Question updated! ✅")
                                        st.session_state.pop('editing_question')
                                        st.rerun()
                        else:
                            st.error("Question and Question Number are required! ⚠️")