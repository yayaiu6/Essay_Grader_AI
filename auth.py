import hashlib
import sqlite3
import database as db

def register_teacher(username: str, password: str) -> bool:
    """
    Register a new teacher in the system.
    
    Important points:
    - Checks if username already exists to prevent duplicates
    - Securely hashes the password using SHA-256 before storage
    - Returns True on successful registration, False if username exists or on error
    """
    try:
        with db.db_connection() as conn:
            cursor = conn.cursor()
            # Check for existing username to maintain uniqueness
            cursor.execute('SELECT username FROM teachers WHERE username = ?', (username,))
            if cursor.fetchone():
                return False
            
            # Hash password for security before storing in database
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert new teacher record with hashed password
            cursor.execute('INSERT INTO teachers (username, password) VALUES (?, ?)', 
                          (username, hashed_password))
            conn.commit()
            return True
    except sqlite3.Error:
        return False

def login_teacher(username: str, password: str) -> bool:
    """
    Verify teacher login credentials.
    
    Important points:
    - Hashes provided password using same SHA-256 algorithm
    - Compares hashed password with stored hash
    - Returns True if credentials match, False otherwise
    - Uses parameterized queries to prevent SQL injection
    """
    try:
        with db.db_connection() as conn:
            cursor = conn.cursor()
            # Hash input password to compare with stored hash
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Verify credentials using secure parameterized query
            cursor.execute('SELECT username FROM teachers WHERE username = ? AND password = ?', 
                          (username, hashed_password))
            return cursor.fetchone() is not None
    except sqlite3.Error:
        return False