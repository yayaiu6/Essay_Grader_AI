# Import required libraries
import streamlit as st
from utils import load_questions
from submission_manager import save_submission
from evaluation import evaluate_answer
import openai
import env
import pandas

# Initialize OpenAI client with API key
client = openai.Client(api_key=env.my_key)

# Get teacher and exam IDs from URL parameters
teacher_id = st.query_params.get("teacher_id", "teacher1")
exam_id = st.query_params.get("exam_id", None)
st.title("Eshraq - Exam Submission 📚")

# Check if exam ID is provided
if not exam_id:
    st.error("No exam specified! Please use a valid exam link. ⚠️")
else:
    # Load questions for the specified exam
    questions = load_questions(teacher_id, exam_id)
    if not questions:
        st.warning("No questions available for this exam yet. Ask your teacher to add some! ⚠️")
    else:
        # Create exam form interface
        with st.form(key="exam_form"):
            student_name = st.text_input("Your Name:", key="student_name")
            answers = {}
            
            # Generate input fields for each question based on its type
            for q_text, q_data in questions.items():
                st.subheader(q_text)
                question_type = q_data.get("type")
                # Handle Short Answer questions
                if question_type == "Short Answer":
                    answers[q_text] = st.text_area("Your answer:", key=f"answer_{q_text}")
                # Handle Multiple Choice questions
                elif question_type == "Multiple Choice":
                    if "options" in q_data:
                        answers[q_text] = st.multiselect("Choose one or more:", q_data["options"], key=f"answer_{q_text}")
                    else:
                        st.error(f"Question '{q_text}' is missing options!")
                        answers[q_text] = None
                else:
                    st.error(f"Question '{q_text}' has an invalid type: {question_type}")
                    answers[q_text] = None
            submit_button = st.form_submit_button("Submit Exam")

        # Handle form submission
        if submit_button:
            student_name = st.session_state["student_name"]
            if not student_name:
                st.error("Please enter your name! ⚠️")
            else:
                # Collect all answers from session state
                answers = {q_text: st.session_state.get(f"answer_{q_text}") for q_text in questions}
                evaluations = {}
                total_score = 0
                max_score = len(questions) * 10

                # Evaluate each answer
                for q_text, answer in answers.items():
                    if answer is None:
                        continue
                    q_data = questions[q_text]
                    
                    # Evaluate Short Answer questions using AI
                    if q_data.get("type") == "Short Answer":
                        if "reference" not in q_data:
                            st.error(f"Question '{q_text}' is missing 'reference' key.")
                            continue
                        eval_result = evaluate_answer(q_text, answer, q_data["reference"])
                        evaluations[q_text] = eval_result
                        total_score += eval_result["score"]
                    
                    # Evaluate Multiple Choice questions
                    elif q_data.get("type") == "Multiple Choice":
                        if "correct" not in q_data or "options" not in q_data:
                            st.error(f"Question '{q_text}' is missing required keys.")
                            continue
                        correct = set(answer) == set(q_data["correct"])  
                        score = 10 if correct else 0
                        feedback = "Correct! ✅" if correct else "Incorrect. Try reviewing this Question! 📖"
                        evaluations[q_text] = {"correct": correct, "score": score, "feedback": feedback}
                        total_score += score

                # Generate performance feedback and topic-wise analysis
                if evaluations:
                    topic_scores = {}
                    for q_text, eval in evaluations.items():
                        topic = questions[q_text].get("Question Number", "General")
                        topic_scores.setdefault(topic, []).append(eval["score"])
                    
                    # Create detailed feedback with performance insights
                    feedback = f"Your total score is {total_score} out of {max_score}.\n\n**Performance Insights:**\n"
                    for topic, scores in topic_scores.items():
                        avg_score = sum(scores) / len(scores)
                        if avg_score < 7:
                            feedback += f"- {topic}: Avg. {avg_score:.1f}/10. Review the basics of {topic}. 📚\n"
                        else:
                            feedback += f"- {topic}: Avg. {avg_score:.1f}/10. Good work—keep practicing! 🌟\n"
                    
                    # Display results and save submission
                    st.write("**Exam Results**")
                    st.write(feedback)

                    # Prepare and save submission data
                    submission = {
                        "student_name": student_name,
                        "answers": answers,
                        "evaluations": evaluations,
                        "total_score": total_score,
                        "max_score": max_score
                    }
                    save_submission(teacher_id, exam_id, submission)
                    st.success("Your answers have been submitted successfully! ✅")
                else:
                    st.error("No valid answers were evaluated. Please check the questions. ⚠️")