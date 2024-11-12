# Flight-Crew-Scheduling-and-Duty-Time-Compliance-System
I developed this crew scheduling system using python streamlit for front end and backend ad sql code.

pip install streamlit mysql-connector-python

# put your sql password and database name in this part of python code
# Connect to MySQL with error handling
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="crew@123",  # Update this to your actual password
            database="CrewManagement"
        )
    

