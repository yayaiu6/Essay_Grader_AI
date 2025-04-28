import streamlit as st
from utils import load_questions
from submission_manager import save_submission
from evaluation import evaluate_answer
from openai import AzureOpenAI
import pandas
import os

# Azure OpenAI configuration
ENDPOINT = os.getenv("ENDPOINT_URL", "https://example-openai-endpoint.com/")  # Azure OpenAI endpoint URL
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "Your-API-Key-Here")  # Azure OpenAI API key
API_VERSION = "2025-01-01-preview"  # API version used
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-4.1")  # Deployment name for the model

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=ENDPOINT,  # Passing the API endpoint URL
    api_key=API_KEY,          # Passing the API key
    api_version=API_VERSION   # Passing the API version
)

# Retrieve teacher ID and exam ID from URL query parameters
teacher_id = st.query_params.get("teacher_id", "teacher1")  # Default teacher ID
exam_id = st.query_params.get("exam_id", None)  # Retrieve exam ID from the URL

# Set the page title
st.title("Eshraq - Exam Submission 📚")

# Check if the exam ID is provided
if not exam_id:
    st.error("No exam specified! Please use a valid exam link. ⚠️")  # Error message for missing exam ID
else:
    questions = load_questions(teacher_id, exam_id)  # Load the exam questions based on teacher and exam IDs
    if not questions:
        st.warning("No questions available for this exam yet. Ask your teacher to add some! ⚠️")  # Warning if no questions are found
    else:
        # Display the exam form
        with st.form(key="exam_form"):
            student_name = st.text_input("Your Name:", key="student_name")  # Field to input student's name
            answers = {}
            for q_text, q_data in questions.items():
                st.subheader(q_text)  # Display the question text
                question_type = q_data.get("type")  # Determine the question type
                if question_type == "Short Answer":
                    answers[q_text] = st.text_area("Your answer:", key=f"answer_{q_text}")  # Text area for short answers
                elif question_type == "Multiple Choice":
                    if "options" in q_data:
                        answers[q_text] = st.multiselect("Choose one or more:", q_data["options"], key=f"answer_{q_text}")  # Multi-select for multiple choice questions
                    else:
                        st.error(f"Question '{q_text}' is missing options!")  # Error if options are missing
                        answers[q_text] = None
                else:
                    st.error(f"Question '{q_text}' has an invalid type: {question_type}")  # Error for invalid question type
                    answers[q_text] = None
            submit_button = st.form_submit_button("Submit Exam")  # Button to submit the exam

        if submit_button:
            student_name = st.session_state["student_name"]  # Retrieve student's name from session state
            if not student_name:
                st.error("Please enter your name! ⚠️")  # Error if student's name is not entered
            else:
                # Collect answers from session state
                answers = {q_text: st.session_state.get(f"answer_{q_text}") for q_text in questions}
                evaluations = {}
                total_score = 0
                max_score = len(questions) * 10  # Maximum possible score

                for q_text, answer in answers.items():
                    if answer is None:
                        continue  # Skip unanswered questions
                    q_data = questions[q_text]
                    if q_data.get("type") == "Short Answer":
                        if "reference" not in q_data:
                            st.error(f"Question '{q_text}' is missing 'reference' key.")  # Error if reference key is missing
                            continue
                        eval_result = evaluate_answer(q_text, answer, q_data["reference"])  # Evaluate short answer
                        evaluations[q_text] = eval_result
                        total_score += eval_result["score"]
                    elif q_data.get("type") == "Multiple Choice":
                        if "correct" not in q_data or "options" not in q_data:
                            st.error(f"Question '{q_text}' is missing required keys.")  # Error if required keys are missing
                            continue
                        correct = set(answer) == set(q_data["correct"])  # Check if the answer is correct
                        score = 10 if correct else 0
                        feedback = "Correct! ✅" if correct else "Incorrect. Try reviewing this Question! 📖"
                        evaluations[q_text] = {"correct": correct, "score": score, "feedback": feedback}
                        total_score += score

                if evaluations:
                    # Calculate topic-wise scores
                    topic_scores = {}
                    for q_text, eval in evaluations.items():
                        topic = questions[q_text].get("Question Number", "General")
                        topic_scores.setdefault(topic, []).append(eval["score"])
                    feedback = f"Your total score is {total_score} out of {max_score}.\n\n**Performance Insights:**\n"
                    for topic, scores in topic_scores.items():
                        avg_score = sum(scores) / len(scores)
                        if avg_score < 7:
                            feedback += f"- {topic}: Avg. {avg_score:.1f}/10. Review the basics of {topic}. 📚\n"
                        else:
                            feedback += f"- {topic}: Avg. {avg_score:.1f}/10. Good work—keep practicing! 🌟\n"
                    st.write("**Exam Results**")
                    st.write(feedback)

                    # Save the submission
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
                    st.error("No valid answers were evaluated. Please check the questions. ⚠️")  # Error if no valid answers
