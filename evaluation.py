import os
from openai import AzureOpenAI
from typing import Dict, Any

# Azure OpenAI configuration
# Retrieve configuration details for Azure OpenAI from environment variables,
# with default values provided for local testing or fallback.
ENDPOINT = os.getenv("ENDPOINT_URL", "https://your_account.openai.azure.com/")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your_azure_openAI_KEY❤️")
API_VERSION = "2025-01-01-preview"
DEPLOYMENT_GPT4 = os.getenv("DEPLOYMENT_NAME_GPT4", "gpt-4.1")

def detect_subject(question: str) -> str:
    """
    Detect the academic subject of a question using Azure OpenAI.

    This function analyzes the given question and classifies it into one of the predefined subjects
    (e.g., Mathematics, Science, History, etc.) by sending the prompt to Azure OpenAI.

    Args:
        question (str): The question to evaluate.

    Returns:
        str: The detected academic subject, or "Other" if detection fails.
    """
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    
    # Prompt instructing the AI to classify the question into a subject category.
    prompt = f"""
    You are an expert in educational content classification. Based on the question provided, identify the academic subject it belongs to. Choose from the following subjects: Mathematics, Science, History, Language, Geography, or Other. Provide only the subject name as the output.
    Question: {question}
    """
    try:
        # Sending the request to Azure OpenAI for subject classification.
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10
        )
        # Extracting and returning the subject from the response.
        subject = response.choices[0].message.content.strip()
        return subject
    except Exception:
        # Fallback to "Other" in case of an error.
        return "Other"

def evaluate_answer(question: str, student_answer: str, reference: str) -> Dict[str, Any]:
    """
    Evaluate a student's answer to a question using Azure OpenAI with subject-specific criteria.

    This function detects the subject of the question, selects evaluation criteria based on the subject,
    and generates a score and feedback using Azure OpenAI.

    Args:
        question (str): The question being evaluated.
        student_answer (str): The student's answer to the question.
        reference (str): The correct or reference answer for the question.

    Returns:
        Dict[str, Any]: A dictionary containing the evaluation result, score, and feedback.
    """
    # Detecting the subject of the question.
    subject = detect_subject(question)
    
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    
    # Predefined evaluation criteria based on the subject.
    subject_criteria = {
        "Mathematics": """
        - Focus on correctness of calculations and logic.
        - Minor spelling errors are irrelevant unless they change the meaning.
        - Award full marks for correct answers even if expressed differently.
        """,
        "Science": """
        - Prioritize scientific accuracy and use of correct terminology.
        - Minor spelling errors should not heavily penalize if the concept is correct.
        - Partial credit for incomplete but relevant answers.
        """,
        "History": """
        - Emphasize factual accuracy and relevance to the question.
        - Allow flexibility in expression as long as key events or concepts are correct.
        - Minor errors in dates or names should not lead to harsh penalties.
        """,
        "Language": """
        - Focus on grammar, vocabulary, and clarity of expression.
        - Award marks for coherent ideas even with minor mistakes.
        """,
        "Geography": """
        - Prioritize accuracy of locations, terms, and concepts.
        - Minor spelling errors in names are acceptable if the context is clear.
        - Partial credit for partially correct answers.
        """,
        "Other": """
        - Evaluate based on clarity, relevance, and completeness.
        - Be lenient with minor errors unless they significantly alter the meaning.
        """
    }

    # Select appropriate criteria for the detected subject.
    criteria = subject_criteria.get(subject, subject_criteria["Other"])

    # Constructing the prompt to evaluate the student's answer.
    prompt = f"""
    You are an intelligent teacher specialized in educational assessment for {subject}. Evaluate the student's answer based on the following criteria:
    {criteria}
    Your evaluation should be based on the following scale:
    - 8 to 10 points for answers that are fully accurate, clear, and complete in relation to the reference answer.
    - 5 to 7 points for answers that are partially correct with minor errors or omissions, but still convey the main idea effectively.
    - 0 to 4 points for answers that are incorrect, off-topic, or fail to address the question.
    Output Format:
    Score: [X/10]
    Feedback: [Detailed feedback]
    Guidelines:
    - If the answer is substantially correct, even with slight differences in wording or phrasing, assess it fairly as correct or partially correct.
    - Do not penalize for minor differences in expression, as long as the main idea is conveyed clearly and accurately.
    Question: {question}
    Reference Answer: {reference}
    Student Answer: {student_answer}
    """
    try:
        # Sending the evaluation request to Azure OpenAI.
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        # Parsing the response to extract score and feedback.
        response_text = response.choices[0].message.content
        lines = response_text.split("\n")
        result = {"correct": False, "score": 0, "feedback": ""}
        for line in lines:
            if line.startswith("Score:"):
                result["score"] = int(line.split(":")[1].strip().split("/")[0])
                result["correct"] = result["score"] >= 8
            elif line.startswith("Feedback:"):
                result["feedback"] = line.split(":")[1].strip()
        return result
    except Exception as e:
        # Handle potential errors during evaluation.
        print(f"Evaluation error: {e}")
        return {"correct": False, "score": 0, "feedback": "Error in evaluation"}

def generate_student_feedback(student_name: str, answers: Dict[str, str], evaluations: Dict[str, Dict[str, Any]], total_score: int, max_score: int) -> str:
    """
    Generate detailed feedback for a student based on their answers and evaluations.

    This function compiles a report summarizing the student's overall performance, including
    specific feedback for each question, and provides recommendations for improvement.

    Args:
        student_name (str): The name of the student.
        answers (Dict[str, str]): A dictionary of questions and the student's answers.
        evaluations (Dict[str, Dict[str, Any]]): A dictionary of evaluation results for each question.
        total_score (int): The total score obtained by the student.
        max_score (int): The maximum possible score.

    Returns:
        str: A detailed feedback report for the student.
    """
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    
    # Constructing the prompt for generating feedback.
    prompt = f"""
    You are an expert in evaluating student responses. Based on the following data, provide a comprehensive and short report on the student's performance for the teacher. The report should include:
    - A brief evaluation of the student's overall performance.
    - Suggestions for improvement based on specific weaknesses.
    Student Name: {student_name}
    Total Result: {total_score}/{max_score}
    """
    for q_text, answer in answers.items():
        eval_data = evaluations.get(q_text, {"score": 0, "feedback": "Not evaluated"})
        prompt += f"- Question: {q_text}\n  Student Answer: {answer}\n  Score: {eval_data['score']}/10\n  Feedback: {eval_data['feedback']}\n"

    prompt += "Provide the feedback in a clear and concise format, suitable for a teacher to review."

    try:
        # Sending the feedback generation request to Azure OpenAI.
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=100
        )
        # Returning the generated feedback.
        return response.choices[0].message.content
    except Exception:
        # Handle potential errors during feedback generation.
        return "Error generating feedback."
