import sqlite3
import os
from contextlib import contextmanager

# Create a data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

DB_PATH = 'data/eshraq.db'

def get_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_PATH, timeout=2.0)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_connection():
    """Context manager for database connections to ensure proper closing"""
    conn = None
    try:
        conn = get_connection()
        yield conn
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database by creating necessary tables if they don't exist"""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')

        # Teachers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        ''')

        # Exams table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            exam_name TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers (username),
            UNIQUE (teacher_id, exam_name)
        )
        ''')

        # Questions table with exam_id
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            question_number TEXT NOT NULL,
            reference TEXT,
            options TEXT,
            correct_option TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers (username),
            FOREIGN KEY (exam_id) REFERENCES exams (id),
            UNIQUE (teacher_id, exam_id, question_text)
        )
        ''')

        # Submissions table with exam_id
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            exam_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            submission_data TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers (username),
            FOREIGN KEY (exam_id) REFERENCES exams (id)
        )
        ''')

        conn.commit()

init_db()