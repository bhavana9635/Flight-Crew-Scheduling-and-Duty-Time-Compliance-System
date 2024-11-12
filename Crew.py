import streamlit as st
import mysql.connector
import hashlib
from datetime import datetime

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to MySQL with error handling
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Bhavana@9635",  # Update this to your actual password
            database="CrewManagement"
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

    # Add Logout Button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_type = ""
        st.success("Logged out successfully!")

    if st.session_state.user_type == "Admin":
       admin_homepage()
    elif st.session_state.user_type == "CrewMember":
        crew_member_homepage()

# Crew Member's home page function
def crew_member_homepage():
    st.header("Crew Member Dashboard")
    st.write("View your assignments, duty logs, and regulations.")
    
    # View Assignments
    if st.button("View Assignments"):
        assignments = fetch_query("SELECT * FROM CrewAssignment WHERE crew_id = %s", (st.session_state.user_name,))
        if assignments:
            for assignment in assignments:
                flight_info = fetch_query("SELECT flight_number, departure, arrival FROM Flight WHERE flight_id = %s", (assignment[2],))
                st.write(f"Assignment ID: {assignment[0]}, Flight: {flight_info[0][0]}, Departure: {flight_info[0][1]}, Arrival: {flight_info[0][2]}, Date: {assignment[3]}")
        else:
            st.write("No assignments found.")

    # View Duty Logs
    if st.button("View Duty Logs"):
        duty_logs = fetch_query("SELECT * FROM DutyLog WHERE crew_id = %s", (st.session_state.user_name,))
        if duty_logs:
            for log in duty_logs:
                flight_info = fetch_query("SELECT flight_number, departure, arrival FROM Flight WHERE flight_id = %s", (log[2],))
                st.write(f"Duty Log ID: {log[0]}, Flight: {flight_info[0][0]}, Date: {log[3]}, Status: {log[4]}")
        else:
            st.write("No duty logs found.")

    # View Regulations
    if st.button("View Regulations"):
        regulations = fetch_query("SELECT * FROM Regulation")
        if regulations:
            for regulation in regulations:
                st.write(f"Regulation ID: {regulation[0]}, Name: {regulation[1]}, Description: {regulation[2]}")
        else:
            st.write("No regulations found.")


# Admin's home page function
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

# Manage Crew Members
def manage_crew_members():
    action = st.selectbox("Select Action", ["Add Crew Member", "Update Crew Member", "Delete Crew Member", "View Crew Members"])

    if action == "Add Crew Member":
        st.subheader("Add Crew Member")
        with st.form("add_crew_member"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth")
            role = st.text_input("Role")
            hire_date = st.date_input("Hire Date")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Add Crew Member"):
                crew_member_register(first_name, last_name, dob, role, hire_date, email, phone, password)
                st.success("Crew Member added successfully!")

    elif action == "Update Crew Member":
        st.subheader("Update Crew Member")
        with st.form("update_crew_member"):
            crew_id = st.number_input("Crew ID", min_value=1)
            new_first_name = st.text_input("New First Name")
            new_last_name = st.text_input("New Last Name")
            new_dob = st.date_input("New Date of Birth")
            new_role = st.text_input("New Role")
            new_email = st.text_input("New Email")
            new_phone = st.text_input("New Phone")

            if st.form_submit_button("Update Crew Member"):
                query = "UPDATE CrewMember SET first_name = %s, last_name = %s, date_of_birth = %s, crew_role = %s, email = %s, phone_number = %s WHERE crew_id = %s"
                data = (new_first_name, new_last_name, new_dob, new_role, new_email, new_phone, crew_id)
                execute_query(query, data)
                st.success("Crew Member updated successfully!")

    elif action == "Delete Crew Member":
        st.subheader("Delete Crew Member")
        crew_id = st.number_input("Crew ID", min_value=1)

        if st.button("Delete Crew Member"):
            query = "DELETE FROM CrewMember WHERE crew_id = %s"
            execute_query(query, (crew_id,))
            st.success("Crew Member deleted successfully!")

    elif action == "View Crew Members":
        st.subheader("Crew Members List")
        crew_members = fetch_query("SELECT * FROM CrewMember")
        for member in crew_members:
            st.write(f"ID: {member[0]}, Name: {member[1]} {member[2]}, Role: {member[4]}, Email: {member[6]}, Phone: {member[7]}, Status: {member[9]}")

# Manage Flights
def manage_flights():
    action = st.selectbox("Select Action", ["Add Flight", "Update Flight", "Delete Flight", "View Flights"])

    if action == "Add Flight":
        st.subheader("Add Flight")
        with st.form("add_flight"):
            flight_number = st.text_input("Flight Number")
            departure = st.text_input("Departure")
            arrival = st.text_input("Arrival")
            status = st.text_input("Status")
            if st.form_submit_button("Add Flight"):
                query = "INSERT INTO Flight (flight_number, departure, arrival, status) VALUES (%s, %s, %s, %s)"
                data = (flight_number, departure, arrival, status)
                execute_query(query, data)
                st.success("Flight added successfully!")

    elif action == "Update Flight":
        st.subheader("Update Flight")
        flight_id = st.number_input("Flight ID", min_value=1)
        new_flight_number = st.text_input("New Flight Number")
        new_status = st.text_input("New Status")

        if st.button("Update Flight"):
            query = "UPDATE Flight SET flight_number = %s, status = %s WHERE flight_id = %s"
            data = (new_flight_number, new_status, flight_id)
            execute_query(query, data)
            st.success("Flight updated successfully!")

    elif action == "Delete Flight":
        st.subheader("Delete Flight")
        flight_id = st.number_input("Flight ID", min_value=1)

        if st.button("Delete Flight"):
            query = "DELETE FROM Flight WHERE flight_id = %s"
            execute_query(query, (flight_id,))
            st.success("Flight deleted successfully!")

    elif action == "View Flights":
        st.subheader("Flights List")
        flights = fetch_query("SELECT * FROM Flight")
        for flight in flights:
            st.write(f"ID: {flight[0]}, Flight Number: {flight[1]}, Departure: {flight[2]}, Arrival: {flight[3]}, Status: {flight[4]}")

# Manage Airports
def manage_airports():
    action = st.selectbox("Select Action", ["Add Airport", "Update Airport", "Delete Airport", "View Airports"])

    if action == "Add Airport":
        st.subheader("Add Airport")
        with st.form("add_airport"):
            airport_code = st.text_input("Airport Code")
            airport_name = st.text_input("Airport Name")
            location = st.text_input("Location")
            if st.form_submit_button("Add Airport"):
                query = "INSERT INTO Airport (airport_code, airport_name, location) VALUES (%s, %s, %s)"
                data = (airport_code, airport_name, location)
                execute_query(query, data)
                st.success("Airport added successfully!")

    elif action == "Update Airport":
        st.subheader("Update Airport")
        airport_id = st.number_input("Airport ID", min_value=1)
        new_airport_name = st.text_input("New Airport Name")
        new_location = st.text_input("New Location")

        if st.button("Update Airport"):
            query = "UPDATE Airport SET airport_name = %s, location = %s WHERE airport_id = %s"
            data = (new_airport_name, new_location, airport_id)
            execute_query(query, data)
            st.success("Airport updated successfully!")

    elif action == "Delete Airport":
        st.subheader("Delete Airport")
        airport_id = st.number_input("Airport ID", min_value=1)

        if st.button("Delete Airport"):
            query = "DELETE FROM Airport WHERE airport_id = %s"
            execute_query(query, (airport_id,))
            st.success("Airport deleted successfully!")

    elif action == "View Airports":
        st.subheader("Airports List")
        airports = fetch_query("SELECT * FROM Airport")
        for airport in airports:
            st.write(f"Airport ID: {airport[0]}, Code: {airport[1]}, Name: {airport[2]}, Location: {airport[3]}")

# Manage Crew Assignments
def manage_crew_assignments():
    action = st.selectbox("Select Action", ["Add Crew Assignment", "Update Crew Assignment", "Delete Crew Assignment", "View Crew Assignments"])

    if action == "Add Crew Assignment":
        st.subheader("Add Crew Assignment")
        with st.form("add_assignment"):
            crew_id = st.number_input("Crew ID", min_value=1)
            flight_id = st.number_input("Flight ID", min_value=1)
            assignment_date = st.date_input("Assignment Date")
            if st.form_submit_button("Add Crew Assignment"):
                query = "INSERT INTO CrewAssignment (crew_id, flight_id, assignment_date) VALUES (%s, %s, %s)"
                data = (crew_id, flight_id, assignment_date)
                execute_query(query, data)
                st.success("Crew Assignment added successfully!")

    elif action == "Update Crew Assignment":
        st.subheader("Update Crew Assignment")
        assignment_id = st.number_input("Assignment ID", min_value=1)
        new_flight_id = st.number_input("New Flight ID")
        new_assignment_date = st.date_input("New Assignment Date")

        if st.button("Update Crew Assignment"):
            query = "UPDATE CrewAssignment SET flight_id = %s, assignment_date = %s WHERE assignment_id = %s"
            data = (new_flight_id, new_assignment_date, assignment_id)
            execute_query(query, data)
            st.success("Crew Assignment updated successfully!")

    elif action == "Delete Crew Assignment":
        st.subheader("Delete Crew Assignment")
        assignment_id = st.number_input("Assignment ID", min_value=1)

        if st.button("Delete Crew Assignment"):
            query = "DELETE FROM CrewAssignment WHERE assignment_id = %s"
            execute_query(query, (assignment_id,))
            st.success("Crew Assignment deleted successfully!")

    elif action == "View Crew Assignments":
        st.subheader("Crew Assignments List")
        assignments = fetch_query("SELECT * FROM CrewAssignment")
        for assignment in assignments:
            st.write(f"Assignment ID: {assignment[0]}, Crew ID: {assignment[1]}, Flight ID: {assignment[2]}, Date: {assignment[3]}")

# Manage Crew Leaves
def manage_crew_leaves():
    action = st.selectbox("Select Action", ["Add Crew Leave", "Update Crew Leave", "Delete Crew Leave", "View Crew Leaves"])

    if action == "Add Crew Leave":
        st.subheader("Add Crew Leave")
        with st.form("add_leave"):
            crew_id = st.number_input("Crew ID", min_value=1)
            leave_start = st.date_input("Leave Start Date")
            leave_end = st.date_input("Leave End Date")
            if st.form_submit_button("Add Crew Leave"):
                query = "INSERT INTO CrewLeave (crew_id, leave_start, leave_end) VALUES (%s, %s, %s)"
                data = (crew_id, leave_start, leave_end)
                execute_query(query, data)
                st.success("Crew Leave added successfully!")

    elif action == "Update Crew Leave":
        st.subheader("Update Crew Leave")
        leave_id = st.number_input("Leave ID", min_value=1)
        new_leave_start = st.date_input("New Leave Start Date")
        new_leave_end = st.date_input("New Leave End Date")

        if st.button("Update Crew Leave"):
            query = "UPDATE CrewLeave SET leave_start = %s, leave_end = %s WHERE leave_id = %s"
            data = (new_leave_start, new_leave_end, leave_id)
            execute_query(query, data)
            st.success("Crew Leave updated successfully!")

    elif action == "Delete Crew Leave":
        st.subheader("Delete Crew Leave")
        leave_id = st.number_input("Leave ID", min_value=1)

        if st.button("Delete Crew Leave"):
            query = "DELETE FROM CrewLeave WHERE leave_id = %s"
            execute_query(query, (leave_id,))
            st.success("Crew Leave deleted successfully!")

    elif action == "View Crew Leaves":
        st.subheader("Crew Leaves List")
        leaves = fetch_query("SELECT * FROM CrewLeave")
        for leave in leaves:
            st.write(f"Leave ID: {leave[0]}, Crew ID: {leave[1]}, Start: {leave[2]}, End: {leave[3]}")

# Manage Duty Logs
def manage_duty_logs():
    action = st.selectbox("Select Action", ["Add Duty Log", "Update Duty Log", "Delete Duty Log", "View Duty Logs"])

    if action == "Add Duty Log":
        st.subheader("Add Duty Log")
        with st.form("add_duty_log"):
            crew_id = st.number_input("Crew ID", min_value=1)
            flight_id = st.number_input("Flight ID", min_value=1)
            duty_date = st.date_input("Duty Date")
            duty_status = st.text_input("Duty Status")
            if st.form_submit_button("Add Duty Log"):
                query = "INSERT INTO DutyLog (crew_id, flight_id, duty_date, duty_status) VALUES (%s, %s, %s, %s)"
                data = (crew_id, flight_id, duty_date, duty_status)
                execute_query(query, data)
                st.success("Duty Log added successfully!")

    elif action == "Update Duty Log":
        st.subheader("Update Duty Log")
        duty_log_id = st.number_input("Duty Log ID", min_value=1)
        new_duty_status = st.text_input("New Duty Status")

        if st.button("Update Duty Log"):
            query = "UPDATE DutyLog SET duty_status = %s WHERE duty_log_id = %s"
            data = (new_duty_status, duty_log_id)
            execute_query(query, data)
            st.success("Duty Log updated successfully!")

    elif action == "Delete Duty Log":
        st.subheader("Delete Duty Log")
        duty_log_id = st.number_input("Duty Log ID", min_value=1)

        if st.button("Delete Duty Log"):
            query = "DELETE FROM DutyLog WHERE duty_log_id = %s"
            execute_query(query, (duty_log_id,))
            st.success("Duty Log deleted successfully!")

    elif action == "View Duty Logs":
        st.subheader("Duty Logs List")
        duty_logs = fetch_query("SELECT * FROM DutyLog")
        for log in duty_logs:
            st.write(f"Duty Log ID: {log[0]}, Crew ID: {log[1]}, Flight ID: {log[2]}, Date: {log[3]}, Status: {log[4]}")

# Manage Regulations
def manage_regulations():
    action = st.selectbox("Select Action", ["Add Regulation", "Update Regulation", "Delete Regulation", "View Regulations"])

    if action == "Add Regulation":
        st.subheader("Add Regulation")
        with st.form("add_regulation"):
            regulation_name = st.text_input("Regulation Name")
            description = st.text_area("Description")
            if st.form_submit_button("Add Regulation"):
                query = "INSERT INTO Regulation (regulation_name, description) VALUES (%s, %s)"
                data = (regulation_name, description)
                execute_query(query, data)
                st.success("Regulation added successfully!")

    elif action == "Update Regulation":
        st.subheader("Update Regulation")
        regulation_id = st.number_input("Regulation ID", min_value=1)
        new_regulation_name = st.text_input("New Regulation Name")
        new_description = st.text_area("New Description")

        if st.button("Update Regulation"):
            query = "UPDATE Regulation SET regulation_name = %s, description = %s WHERE regulation_id = %s"
            data = (new_regulation_name, new_description, regulation_id)
            execute_query(query, data)
            st.success("Regulation updated successfully!")

    elif action == "Delete Regulation":
        st.subheader("Delete Regulation")
        regulation_id = st.number_input("Regulation ID", min_value=1)

        if st.button("Delete Regulation"):
            query = "DELETE FROM Regulation WHERE regulation_id = %s"
            execute_query(query, (regulation_id,))
            st.success("Regulation deleted successfully!")

    elif action == "View Regulations":
        st.subheader("Regulations List")
        regulations = fetch_query("SELECT * FROM Regulation")
        for regulation in regulations:
            st.write(f"Regulation ID: {regulation[0]}, Name: {regulation[1]}, Description: {regulation[2]}")

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

# Registration Form for Admin
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
