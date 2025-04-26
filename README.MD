# Essay_Grader_AI

## Overview
"Essay_Grader_AI" is an innovative web application designed to assist teachers in creating and grading essay-based exams using artificial intelligence. Built with Streamlit and powered by OpenAI, this tool allows teachers to manage exams, create questions, and share them with students, while providing automated grading for both short-answer and multiple-choice questions. Students can submit answers through a user-friendly interface and receive immediate feedback, making it a time-saving and efficient solution for educational assessments.

---

## Purpose
- **For Teachers**: Easily create exams, add questions, share exam links with students, and review AI-graded submissions.
- **For Students**: Submit answers through a simple interface and receive instant performance feedback.
- **Key Feature**: Automated grading of short-answer questions using AI with subject-specific evaluation criteria.

---

## Project Structure
The main files in the project include:

### Interface Pages
- **`Home.py`**: The homepage for teacher login and registration using Streamlit.
- **`Teacher.py`**: Teacher dashboard for managing exams, editing questions, and viewing submissions.
- **`Student.py`**: Student interface for submitting exam answers and viewing results.

### Authentication and Database
- **`auth.py`**: Handles user registration and login with SHA-256 password hashing.
- **`database.py`**: Manages SQLite database for storing teacher, exam, question, and submission data.
- **`env.py`**: Stores environment variables, such as the OpenAI API key.

### Exam Management
- **`exam_management.py`**: Interface for managing exams.
- **`question_editor.py`**: Tool for adding and editing questions.
- **`utils.py`**: Utility functions for loading/saving questions and generating exam links.

### Evaluation and Results
- **`evaluation.py`**: Uses OpenAI to evaluate answers based on subject-specific criteria.
- **`submission_manager.py`**: Manages student submission storage.
- **`submission_viewer.py`**: Displays and analyzes student submissions for teachers.

---

## How It Works
1. **Login/Register**: Teachers log in or register via `Home.py`.
2. **Create Exam**: In the teacher dashboard (`Teacher.py`), teachers can create exams and add questions (short-answer or multiple-choice).
3. **Share Exam**: A unique exam link is generated and shared with students.
4. **Submit Answers**: Students access the link in `Student.py` to submit their answers.
5. **Automated Grading**:
   - Short-answer questions are graded using OpenAI, comparing student answers to reference answers.
   - Multiple-choice questions are graded by comparing selected options to correct answers.
6. **Results**: Students receive immediate feedback, and teachers can review submissions in the dashboard.

---

## Technical Details
- **Technologies Used**:
  - **Streamlit**: For creating interactive web interfaces.
  - **SQLite**: Lightweight database for storing data.
  - **OpenAI**: For evaluating short-answer questions using models like GPT-4.1
  - **Python**: Core programming language.
- **Security**:
  - Passwords are hashed using SHA-256 (could be improved with bcrypt).
  - Parameterized SQL queries to prevent SQL injection.
- **Evaluation Features**:
  - Automatic subject detection for questions (e.g., Math, Science) using OpenAI.
  - Subject-specific grading criteria for fair and accurate evaluations.

---

## How to Run or Test the Project
### Local Setup
#### Requirements:
- Python 3.x
- Libraries: `streamlit`, `openai`, `sqlite3`
- OpenAI API key

#### Steps:
1. Install dependencies:
   ```
   pip install streamlit openai
   ```
2. Add your OpenAI API key in `env.py`:
   ```python
   my_key = "your_openai_api_key_here"
   ```
3. Run the application:
   ```
   streamlit run Home.py
   ```

### Online Demo
You can try the project directly via the following link:  
[https://yayaiu6-essay-grader-ai.hf.space/](https://yayaiu6-essay-grader-ai.hf.space/)

---

## Future Improvements
- Enhance security with stronger password hashing (e.g., bcrypt).
- Add statistical analytics for student performance.
- Support more robust databases (e.g., PostgreSQL) for scalability.
- Improve the UI with interactive charts and visualizations.

---

## Final Notes
This project represents a significant effort to create a practical and innovative solution for education. I hope it makes an impact at the Microsoft Hackathon, and I welcome any feedback or suggestions for improvement!

**Developer**: Yahya Mahrouf  
**Connect with Me**: [LinkedIn](https://www.linkedin.com/in/yahya-mahrouf/) | [GitHub](https://github.com/yayaiu6/) | yahyamahroof35@gmail.com
