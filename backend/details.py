from flask import Flask, jsonify, request
import sqlite3
from contextlib import closing
from flask_cors import CORS  # Import the CORS extension

app = Flask(__name__)
CORS(app)  # Enable CORS for your entire app
DB_NAME = 'hospital.db'

def get_db_connection():
    """Create a database connection and return the connection object."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@app.route('/')
def index():
    """Home route with information about available endpoints."""
    return jsonify({
        'message': 'Hospital Management API',
        'available_endpoints': {
            '/appointments': 'GET: Get all appointments or filter by doctor_name with ?doctor_name=X',
            '/appointments/schedule': 'POST: Schedule a new appointment',
            '/patients': 'GET: Get all patients',
            '/doctors': 'GET: Get all doctors'
        }
    })

@app.route('/appointments', methods=['GET'])
def get_appointments():
    """
    Get all appointments or filter by doctor name if provided.
    Query param: doctor_name - Filter appointments by doctor name
    """
    doctor_name = request.args.get('doctor_name')

    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()

            if doctor_name:
                # Get appointments for a specific doctor
                query = '''
                    SELECT
                        a.id, a.patient_name, d.name as doctor_name,
                        d.specialty, a.date, a.time, a.status
                    FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE d.name = ?
                    ORDER BY a.date, a.time
                '''
                cursor.execute(query, (doctor_name,))
            else:
                # Get all appointments
                query = '''
                    SELECT
                        a.id, a.patient_name, d.name as doctor_name,
                        d.specialty, a.date, a.time, a.status
                    FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    ORDER BY a.date, a.time
                '''
                cursor.execute(query)

            appointments = []
            for row in cursor.fetchall():
                appointments.append({
                    'id': row['id'],
                    'patient_name': row['patient_name'],
                    'doctor_name': row['doctor_name'],
                    'specialty': row['specialty'],
                    'date': row['date'],
                    'time': row['time'],
                    'status': row['status']
                })

            print(appointments)

            return jsonify({
                'status': 'success',
                'count': len(appointments),
                'appointments': appointments
            })

    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/appointments/schedule', methods=['POST'])
def schedule_appointment():
    """Schedule a new appointment."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400

    patient_name = data.get('patient_name')
    doctor_name = data.get('doctor_name')
    date = data.get('date')  # Expected format: YYYY-MM-DD
    time = data.get('time')  # Expected format: HH:MM

    if not all([patient_name, doctor_name, date, time]):
        return jsonify({'status': 'error', 'message': 'Missing required fields: patient_name, doctor_name, date, time'}), 400

    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()

            # Get the doctor's ID
            cursor.execute("SELECT id FROM doctors WHERE name = ?", (doctor_name,))
            doctor = cursor.fetchone()
            if not doctor:
                return jsonify({'status': 'error', 'message': f'Doctor "{doctor_name}" not found'}), 404

            doctor_id = doctor['id']

            # Insert the new appointment
            query = "INSERT INTO appointments (patient_name, doctor_id, date, time) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (patient_name, doctor_id, date, time))
            conn.commit()

            new_appointment_id = cursor.lastrowid
            return jsonify({
                'status': 'success',
                'message': 'Appointment scheduled successfully',
                'appointment_id': new_appointment_id,
                'details': {
                    'id': new_appointment_id,
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'date': date,
                    'time': time,
                    'status': 'scheduled'
                }
            }), 201

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/patients')
def get_patients():
    """Get a list of all patients in the system."""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()

            # Get unique patients from appointments table
            query = '''
                SELECT DISTINCT patient_name
                FROM appointments
                ORDER BY patient_name
            '''
            cursor.execute(query)

            patients = []
            for row in cursor.fetchall():
                patients.append(row['patient_name'])

            return jsonify({
                'status': 'success',
                'count': len(patients),
                'patients': patients
            })

    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/doctors')
def get_doctors():
    """Get a list of all doctors in the system."""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()

            query = '''
                SELECT id, name, specialty
                FROM doctors
                ORDER BY name
            '''
            cursor.execute(query)

            doctors = []
            for row in cursor.fetchall():
                doctors.append({
                    'id': row['id'],
                    'name': row['name'],
                    'specialty': row['specialty']
                })

            return jsonify({
                'status': 'success',
                'count': len(doctors),
                'doctors': doctors
            })

    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)