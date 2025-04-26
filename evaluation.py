import openai
import env
from typing import Dict, Any

# This function uses OpenAI to classify questions into academic subjects
def detect_subject(question: str) -> str:
    """Detect the subject of a question using Open AI."""
    client = openai.Client(api_key=env.my_key)
    # Prompt engineering to ensure accurate subject classification
    prompt = f"""
    You are an expert in educational content classification. Based on the question provided, identify the academic subject it belongs to. Choose from the following subjects: Mathematics, Science, History, Language, Geography, or Other. Provide only the subject name as the output.

    Question: {question}
    """
    try:
        # Using GPT-4.1 mini model for efficient subject detection
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10
        )
        subject = response.choices[0].message.content.strip()
        return subject
    except Exception:
        return "Other"  # Fallback to generic criteria if classification fails

def evaluate_answer(question: str, student_answer: str, reference: str) -> Dict[str, Any]:
    """Evaluate a student's answer using Open AI with subject-specific criteria."""
    # First detect the subject to apply appropriate evaluation criteria
    subject = detect_subject(question)
    client = openai.Client(api_key=env.my_key)
    
    # Define subject-specific evaluation criteria for fair assessment
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

    # Select appropriate criteria based on detected subject
    criteria = subject_criteria.get(subject, subject_criteria["Other"])

    # Construct a detailed prompt for the AI evaluator
    prompt = f"""
    You are an intelligent teacher specialized in educational assessment for {subject}. Evaluate the student's answer based on the following criteria:
    {criteria}

    # Scoring guidelines (8-10: excellent, 5-7: satisfactory, 0-4: needs improvement)
    Your evaluation should be based on the following scale:
    - 8 to 10 points for answers that are fully accurate, clear, and complete in relation to the reference answer.
    - 5 to 7 points for answers that are partially correct with minor errors or omissions, but still convey the main idea effectively.
    - 0 to 4 points for answers that are incorrect, off-topic, or fail to address the question.
    """
    try:
        # Use GPT-4 mini model for detailed evaluation
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        # Parse the AI response into structured feedback
        response_text = response.choices[0].message.content
        lines = response_text.split("\n")
        result = {"correct": False, "score": 0, "feedback": ""}
        
        # Extract score and feedback from the response
        for line in lines:
            if line.startswith("Score:"):
                result["score"] = int(line.split(":")[1].strip().split("/")[0])
                result["correct"] = result["score"] >= 8  # Consider scores 8+ as correct
            elif line.startswith("Feedback:"):
                result["feedback"] = line.split(":")[1].strip()
        return result
    except Exception as e:
        print(f"Evaluation error: {e}")
        return {"correct": False, "score": 0, "feedback": "Error in evaluation"}

# Function to generate comprehensive feedback report for teachers
def generate_student_feedback(student_name: str, answers: Dict[str, str], evaluations: Dict[str, Dict[str, Any]], total_score: int, max_score: int) -> str:
    """Generate detailed feedback for a student using Open AI."""
    client = openai.Client(api_key=env.my_key)
    
    # Create a comprehensive prompt including all student data
    prompt = f"""
    You are an expert in evaluating student responses. Based on the following data, provide a comprehensive and short report on the student's performance for the teacher. The report should include:
    - A brief evaluation of the student's overall performance.
    - Suggestions for improvement based on specific weaknesses.

    Student Name: {student_name}
    Total Result: {total_score}/{max_score}
    """
    
    # Add individual question analysis to the prompt
    for q_text, answer in answers.items():
        eval_data = evaluations.get(q_text, {"score": 0, "feedback": "Not evaluated"})
        prompt += f"- Question: {q_text}\n  Student Answer: {answer}\n  Score: {eval_data['score']}/10\n  Feedback: {eval_data['feedback']}\n"

    try:
        # Generate personalized feedback using GPT-4 nano
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception:
        return "Error generating feedback."