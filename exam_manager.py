import database as db
from typing import Dict
import sqlite3

# Function to retrieve all exams associated with a specific teacher
def load_exams(teacher_id: str) -> Dict[int, str]:
    """Load all exams for a specific teacher."""
    try:
        with db.db_connection() as conn:  # Establish database connection using context manager
            cursor = conn.cursor()
            # SQL query to select exam IDs and names for the given teacher
            cursor.execute('SELECT id, exam_name FROM exams WHERE teacher_id = ?', (teacher_id,))
            # Create a dictionary with exam ID as key and exam name as value
            return {row['id']: row['exam_name'] for row in cursor.fetchall()}
    except sqlite3.Error:  # Handle any database errors gracefully
        return {}  # Return empty dictionary if database operation fails

# Function to create a new exam in the database
def save_exam(teacher_id: str, exam_name: str) -> int:
    """Save a new exam."""
    try:
        with db.db_connection() as conn:  # Establish database connection using context manager
            cursor = conn.cursor()
            # SQL query to insert new exam with teacher ID and exam name
            cursor.execute('INSERT INTO exams (teacher_id, exam_name) VALUES (?, ?)', 
                          (teacher_id, exam_name))
            conn.commit()  # Commit the transaction to save changes
            return cursor.lastrowid  # Return the ID of the newly created exam
    except sqlite3.Error:  # Handle any database errors gracefully
        return None  # Return None if database operation fails