import sqlite3
from models import DB_NAME
from contextlib import closing

def add_doctor():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    doctor_data = (
        "Dr. John Doe",           # Name
        "doctor@example.com",     # Email
        "doctor123", # Hashed Password
        "9876543210",             # Phone
        "Hyderabad",              # Location
        "doctor"                  # Role
    )

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, location, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, doctor_data)
        conn.commit()
        print("Doctor added successfully!")
    except sqlite3.IntegrityError:
        print("Doctor already exists!")
    
    conn.close()

# Run the function
add_doctor()

# Fetch and display all doctors
with closing(sqlite3.connect(DB_NAME)) as conn:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE role='doctor'")  # ✅ FIXED QUERY
    rows = c.fetchall()
    for row in rows:
        print(dict(row))  # ✅ Convert Row object to a dictionary for better readability


def add_patient():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    patient_data = (
        "John Doe",           # Name
        "john@example.com",     # Email 
        "patient123", # Hashed Password
        "9876543210",             # Phone
        "Hyderabad",              # Location
        "patient"                  # Role
    )   
    
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, location, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, patient_data)
        conn.commit()   
        print("Patient added successfully!")
    except sqlite3.IntegrityError:
        print("Patient already exists!")
    
    conn.close()

# Run the function
add_patient() 


with closing(sqlite3.connect(DB_NAME)) as conn:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE role='patient'")  # ✅ FIXED QUERY
    rows = c.fetchall()
    for row in rows:
        print(dict(row))   