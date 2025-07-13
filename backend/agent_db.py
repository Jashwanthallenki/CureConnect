import sqlite3
from contextlib import closing

DB_NAME = 'hospital.db'

def init_db():
    """Initialize the database with tables and sample data if empty."""
    try:
        with closing(sqlite3.connect(DB_NAME)) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign keys are enforced
            c = conn.cursor()
            
            # Create doctors table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL UNIQUE, 
                    specialty TEXT NOT NULL
                )
            ''')

            # Create appointments table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    patient_name TEXT NOT NULL, 
                    doctor_id INTEGER NOT NULL, 
                    date TEXT NOT NULL,       -- Format: YYYY-MM-DD
                    time TEXT NOT NULL,       -- Format: HH:MM
                    status TEXT CHECK(status IN ('scheduled', 'completed', 'canceled')) DEFAULT 'scheduled',  
                    FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
                )
            ''')

            # Insert sample doctor data (if table is empty)
            c.execute("SELECT COUNT(*) FROM doctors")
            if c.fetchone()[0] == 0:
                doctors_data = [
                    ('Dr. John Doe', 'Cardiologist'),
                    ('Dr. Alice Smith', 'Dermatologist'),
                    ('Dr. Robert Brown', 'Neurologist'),
                    ('Dr. Emily White', 'Pediatrician'),
                    ('Dr. Mark Green', 'Orthopedic'),
                    ('Dr. Sarah Lee', 'General Physician')
                ]
                c.executemany("INSERT INTO doctors (name, specialty) VALUES (?, ?)", doctors_data)

            # Insert sample appointments data (if empty)
            c.execute("SELECT COUNT(*) FROM appointments")
            if c.fetchone()[0] == 0:
                appointments_data = [
                    ('Alice', 1, '2025-04-01', '10:30', 'scheduled'),
                    ('Bob', 1, '2025-04-02', '14:00', 'scheduled'),
                    ('Charlie', 2, '2025-04-03', '09:00', 'scheduled'),
                    ('David', 4, '2025-04-01', '13:00', 'scheduled'),
                    ('Eve', 6, '2025-04-02', '11:00', 'scheduled')
                ]
                c.executemany(
                    "INSERT INTO appointments (patient_name, doctor_id, date, time, status) VALUES (?, ?, ?, ?, ?)",
                    appointments_data
                )

            conn.commit()
            print("Database initialized successfully!")

    except sqlite3.Error as e:
        print(f"SQLite error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


# Run database initialization
if __name__ == "__main__":
    init_db()
