import os
from openai import AzureOpenAI
from typing import Dict, Any

# Azure OpenAI configuration
ENDPOINT = os.getenv("ENDPOINT_URL", "https://yahya-ma1c3o0m-eastus2.openai.azure.com/")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your_azure_openAI_KEY❤️")
API_VERSION = "2025-01-01-preview"
DEPLOYMENT_GPT4 = os.getenv("DEPLOYMENT_NAME_GPT4", "gpt-4.1")

def detect_subject(question: str) -> str:
    """Detect the subject of a question using Azure OpenAI."""
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    prompt = f"""
    You are an expert in educational content classification. Based on the question provided, identify the academic subject it belongs to. Choose from the following subjects: Mathematics, Science, History, Language, Geography, or Other. Provide only the subject name as the output.
    Question: {question}
    """
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10
        )
        subject = response.choices[0].message.content.strip()
        return subject
    except Exception:
        return "Other"

def evaluate_answer(question: str, student_answer: str, reference: str) -> Dict[str, Any]:
    """Evaluate a student's answer using Azure OpenAI with subject-specific criteria."""
    subject = detect_subject(question)
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    
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

    criteria = subject_criteria.get(subject, subject_criteria["Other"])

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
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
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
        print(f"Evaluation error: {e
}")
        return {"correct": False, "score": 0, "feedback": "Error in evaluation"}

def generate_student_feedback(student_name: str, answers: Dict[str, str], evaluations: Dict[str, Dict[str, Any]], total_score: int, max_score: int) -> str:
    """Generate detailed feedback for a student using Azure OpenAI."""
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )
    
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
        response = client.chat.completions.create(
            model=DEPLOYMENT_GPT4,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception:
        return "Error generating feedback."
