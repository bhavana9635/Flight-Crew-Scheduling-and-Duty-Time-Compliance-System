import streamlit as st
import hashlib
from datetime import datetime

# Try importing MySQL connector with friendly error if missing
try:
    import mysql.connector
except ImportError:
    st.error("MySQL Connector is not installed. Please run:\n\npip install mysql-connector-python")
    st.stop()

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to MySQL using st.secrets (no hardcoding)
def connect_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None

# Execute a query
def execute_query(query, data=None):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            connection.commit()
        except mysql.connector.Error as err:
            st.error(f"Error executing query: {err}")
        finally:
            cursor.close()
            connection.close()

# Fetch data from a query
def fetch_query(query, data=None):
    connection = connect_db()
    result = []
    if connection:
        cursor = connection.cursor()
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            st.error(f"Error fetching data: {err}")
        finally:
            cursor.close()
            connection.close()
    return result

# Admin login logic
def admin_login(email, password):
    hashed_password = hash_password(password)
    query = "SELECT * FROM Admin WHERE email = %s AND password = %s"
    data = (email, hashed_password)
    result = fetch_query(query, data)
    if result:
        st.session_state.logged_in = True
        st.session_state.user_type = "Admin"
        st.session_state.user_name = result[0][1]  # Assuming name is in the second column
    return result

# Crew Member login logic
def crew_member_login(email, password):
    hashed_password = hash_password(password)
    query = "SELECT * FROM CrewMember WHERE email = %s AND password = %s"
    data = (email, hashed_password)
    result = fetch_query(query, data)
    if result:
        st.session_state.logged_in = True
        st.session_state.user_type = "CrewMember"
        st.session_state.user_name = result[0][1]  # Assuming name is in the second column
    return result

# Registration functions
def admin_register(name, email, phone, password):
    hashed_password = hash_password(password)
    query = "INSERT INTO Admin (name, email, phone, password) VALUES (%s, %s, %s, %s)"
    data = (name, email, phone, hashed_password)
    execute_query(query, data)

def crew_member_register(first_name, last_name, dob, role, hire_date, email, phone, password):
    hashed_password = hash_password(password)
    query = """INSERT INTO CrewMember (first_name, last_name, date_of_birth, crew_role, hire_date, email, 
               phone_number, status, password) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active', %s)"""
    data = (first_name, last_name, dob, role, hire_date, email, phone, hashed_password)
    execute_query(query, data)

# Home Page After Login
def homepage():
    st.title(f"Welcome {st.session_state.user_name}!")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_type = ""
        st.success("Logged out successfully!")

    if st.session_state.user_type == "Admin":
        admin_homepage()
    elif st.session_state.user_type == "CrewMember":
        crew_member_homepage()

# Crew Member's home page
def crew_member_homepage():
    st.header("Crew Member Dashboard")
    st.write("View your assignments, duty logs, and regulations.")
    
    if st.button("View Assignments"):
        assignments = fetch_query("SELECT * FROM CrewAssignment WHERE crew_id = %s", (st.session_state.user_name,))
        if assignments:
            for assignment in assignments:
                flight_info = fetch_query("SELECT flight_number, departure, arrival FROM Flight WHERE flight_id = %s", (assignment[2],))
                st.write(f"Assignment ID: {assignment[0]}, Flight: {flight_info[0][0]}, Departure: {flight_info[0][1]}, Arrival: {flight_info[0][2]}, Date: {assignment[3]}")
        else:
            st.write("No assignments found.")

    if st.button("View Duty Logs"):
        duty_logs = fetch_query("SELECT * FROM DutyLog WHERE crew_id = %s", (st.session_state.user_name,))
        if duty_logs:
            for log in duty_logs:
                flight_info = fetch_query("SELECT flight_number, departure, arrival FROM Flight WHERE flight_id = %s", (log[2],))
                st.write(f"Duty Log ID: {log[0]}, Flight: {flight_info[0][0]}, Date: {log[3]}, Status: {log[4]}")
        else:
            st.write("No duty logs found.")

    if st.button("View Regulations"):
        regulations = fetch_query("SELECT * FROM Regulation")
        if regulations:
            for regulation in regulations:
                st.write(f"Regulation ID: {regulation[0]}, Name: {regulation[1]}, Description: {regulation[2]}")
        else:
            st.write("No regulations found.")

# Admin's home page (other management functions remain unchanged)
def admin_homepage():
    st.header("Admin Dashboard")
    action = st.selectbox("Select Action", ["Manage Crew Members", "Manage Flights", "Manage Airports", 
                                             "Manage Crew Assignments", "Manage Crew Leaves", 
                                             "Manage Duty Logs", "Manage Regulations"])

    if action == "Manage Crew Members":
        manage_crew_members()
    elif action == "Manage Flights":
        manage_flights()
    elif action == "Manage Airports":
        manage_airports()
    elif action == "Manage Crew Assignments":
        manage_crew_assignments()
    elif action == "Manage Crew Leaves":
        manage_crew_leaves()
    elif action == "Manage Duty Logs":
        manage_duty_logs()
    elif action == "Manage Regulations":
        manage_regulations()

# (The rest of your manage_... functions remain the same)
# -------------------------------------------------------------------------
# Sidebar for Login and Registration
def sidebar():
    st.sidebar.title("Welcome!")
    choice = st.sidebar.radio("Choose an option", ("Login", "Register"))

    if choice == "Login":
        login_form()
    elif choice == "Register":
        register_form()

# Login Form
def login_form():
    login_type = st.selectbox("Login as", ("Admin", "Crew Member"))
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_type == "Admin":
            if admin_login(email, password):
                st.session_state.logged_in = True
                st.session_state.user_type = "Admin"
                st.session_state.page = "admin_homepage"
            else:
                st.error("Invalid credentials!")
        elif login_type == "Crew Member":
            if crew_member_login(email, password):
                st.session_state.logged_in = True
                st.session_state.user_type = "CrewMember"
                st.session_state.page = "crew_member_homepage"
            else:
                st.error("Invalid credentials!")

# Registration Form
def register_form():
    register_type = st.selectbox("Register as", ("Admin", "Crew Member"))

    if register_type == "Admin":
        st.subheader("Register Admin")
        with st.form("register_admin"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Register"):
                admin_register(name, email, phone, password)
                st.success("Admin registered successfully!")

    elif register_type == "Crew Member":
        st.subheader("Register Crew Member")
        with st.form("register_crew_member"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth")
            role = st.text_input("Role")
            hire_date = st.date_input("Hire Date")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Register"):
                crew_member_register(first_name, last_name, dob, role, hire_date, email, phone, password)
                st.success("Crew Member registered successfully!")

# Main program
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    homepage()
else:
    sidebar()
