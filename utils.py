import json
import urllib.parse
import database as db
from typing import Dict, Any
import sqlite3

def load_questions(teacher_id: str, exam_id: int) -> Dict[str, Dict[str, Any]]:
    """Load questions for a specific exam."""
    # Main function to retrieve questions from database for a specific teacher and exam
    try:
        with db.db_connection() as conn:
            cursor = conn.cursor()
            # SQL query to get all question details for the specified exam
            cursor.execute(''' 
            SELECT question_text, question_type, question_number, reference, options, correct_option 
            FROM questions WHERE teacher_id = ? AND exam_id = ?
            ''', (teacher_id, exam_id))
            
            questions = {}
            # Process each question row from database
            for row in cursor.fetchall():
                # Create basic question data structure
                question_data = {
                    "type": row['question_type'],
                    "Question Number": row['question_number']
                }
                
                # Handle different question types
                if row['question_type'] == "Short Answer":
                    # For short answer questions, include reference answer
                    question_data["reference"] = row['reference']
                elif row['question_type'] == "Multiple Choice":
                    # For multiple choice, parse options and correct answers from JSON
                    question_data["options"] = json.loads(row['options']) if row['options'] else []
                    correct_options = json.loads(row['correct_option']) if row['correct_option'] else []
                    question_data["correct"] = correct_options
                
                # Store question using question text as key
                questions[row['question_text']] = question_data
            return questions
    except sqlite3.Error:
        return {}

def save_questions(teacher_id: str, exam_id: int, questions: Dict[str, Dict[str, Any]]) -> bool:
    """Save questions for a specific exam."""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        # First delete existing questions for this exam
        cursor.execute('DELETE FROM questions WHERE teacher_id = ? AND exam_id = ?', 
                      (teacher_id, exam_id))
        
        # Insert each question into database
        for question_text, data in questions.items():
            # Handle correct options for multiple choice questions
            if data['type'] == "Multiple Choice":
                correct_options = json.dumps(data.get('correct', []))
            else:
                correct_options = None
                
            # Insert new question with all its details
            cursor.execute(''' 
                INSERT INTO questions 
                (teacher_id, exam_id, question_text, question_type, question_number, reference, options, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                teacher_id,
                exam_id,
                question_text,
                data['type'],
                data.get('Question Number', 'General'),
                data.get('reference'),
                json.dumps(data.get('options', [])),
                correct_options
            ))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        # Ensure connection is closed even if error occurs
        conn.close()

def generate_exam_link(teacher_id: str, exam_id: str) -> str:
    """Generate a unique exam link with proper URL encoding."""
    # URL encode the IDs to handle special characters
    encoded_teacher_id = urllib.parse.quote(str(teacher_id)) 
    encoded_exam_id = urllib.parse.quote(str(exam_id)) 
    # Generate and return the complete exam URL
    return f"http://localhost:8501/Student?teacher_id={encoded_teacher_id}&exam_id={encoded_exam_id}"
    # you can change your url by changing this "http://localhost:8501"