import json
import sqlite3
import database as db
from typing import List, Dict, Any

# Function to retrieve exam submissions from database
def load_submissions(teacher_id: str, exam_id: int) -> List[Dict[str, Any]]:
    """Load submissions for a specific exam."""
    try:
        with db.db_connection() as conn:  # Using context manager for auto-closing connection
            cursor = conn.cursor()
            # Query to fetch submission data based on teacher and exam IDs
            cursor.execute('SELECT submission_data FROM submissions WHERE teacher_id = ? AND exam_id = ?', 
                          (teacher_id, exam_id))
            # Convert JSON strings back to Python dictionaries for each submission
            return [json.loads(row['submission_data']) for row in cursor.fetchall()]
    except sqlite3.Error:
        # Return empty list if database operation fails
        return []

# Function to store new exam submissions in database
def save_submission(teacher_id: str, exam_id: int, submission: Dict[str, Any]) -> bool:
    """Save a submission for a specific exam."""
    try:
        with db.db_connection() as conn:  # Using context manager for auto-closing connection
            cursor = conn.cursor()
            # Convert submission dictionary to JSON string for storage
            submission_json = json.dumps(submission, ensure_ascii=False)  # Allow non-ASCII characters
            # Insert submission details into database
            cursor.execute(''' 
            INSERT INTO submissions (teacher_id, exam_id, student_name, submission_data)
            VALUES (?, ?, ?, ?)
            ''', (teacher_id, exam_id, submission['student_name'], submission_json))
            conn.commit()  # Commit the transaction
            return True  # Return success
    except sqlite3.Error:
        # Return False if database operation fails
        return False