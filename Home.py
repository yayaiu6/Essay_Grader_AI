import streamlit as st
from auth import login_teacher, register_teacher
import database as db




    # Display the main application title with custom styling
st.markdown(
        "<h1 style='text-align: center; color: #708090; font-size: 50px; margin-top: -9px;'>Essay_Grader_AI</h1>",
        unsafe_allow_html=True
)


# Display the application tagline
st.markdown(
    "<p style='text-align: left; color: #7f8c8d; font-size: 18px; margin-top: 10px;'>Create essay Exams and grade them in minutes – not hours</p>",
    unsafe_allow_html=True
)

# Initialize session state variables for user authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["teacher_id"] = None

# Display login/register interface if user is not logged in
if not st.session_state["logged_in"]:
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "create new account"])
    
    # Login tab content
    with tab1:
        st.subheader("Teacher Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            # Verify login credentials and update session state
            if login_teacher(username, password):
                st.session_state["logged_in"] = True
                st.session_state["teacher_id"] = username
                st.success("Logged in successfully! ✅")
                st.rerun()
            else:
                st.error("create account first ⚠️")

    # Registration tab content
    with tab2:
        st.subheader("Register as Teacher")
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        if st.button("Register"):
            # Attempt to register new user
            if register_teacher(new_username, new_password):
                st.success("Registered successfully! Please login. ✅")
            else:
                st.error("Username already exists! ⚠️")
else:
    # Display welcome message and dashboard link for logged-in users
    st.write(f"Welcome, MR.{st.session_state['teacher_id']}!")
    st.page_link("pages/Teacher.py", label="Press here to Teacher Dashboard", use_container_width=True)
    
    # Custom CSS styling for the dashboard link button
    st.markdown("""
        <style>
        [data-testid="stPageLink"] {
            background-color: #007BFF;
            color: white;
            border-radius: 4px;
            padding: 10px;
            text-align: center;
            margin: 10px 0;
            font-weight: bold;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease;
        }
        [data-testid="stPageLink"]:hover {
            background-color: #0056b3;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Logout button functionality
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["teacher_id"] = None
        st.rerun()

# Footer section with social media links and creator information
st.markdown("""
    <div style="text-align: center; font-size: 12px; color: #666; margin-top: 20px;">
        Created by Yahya Mahrouf<br>
        <span style="font-size: 14px; color: #808080; margin-right: 10px;">Connect with Me :</span>
        <a href="https://www.linkedin.com/in/yahya-mahrouf/" target="_blank">
            <img src="https://static.vecteezy.com/system/resources/previews/017/339/624/original/linkedin-icon-free-png.png" width="35" style="vertical-align: middle; margin: 0 5px;">
        </a>
        <a href="https://github.com/yayaiu6/" target="_blank">
            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="vertical-align: middle; margin: 0 5px;">
        </a>
        <a href="https://wa.me/201001866276" target="_blank">
            <img src="https://cdn3.iconfinder.com/data/icons/social-media-chamfered-corner/154/whatsapp-512.png" width="20" style="vertical-align: middle; margin: 0 5px;">
        </a>
    </div>
""", unsafe_allow_html=True)




# Command to run the Streamlit application
# To run code: python -m streamlit run "location_file\Essay_Grader_AI\Home.py"
# Example : python -m streamlit run "C:\Users\yahya\WORK\Essay_Grader_AI\Home.py"