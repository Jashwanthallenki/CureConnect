from flask import Blueprint, request, jsonify
import sqlite3
from models import DB_NAME

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    patient_id, doctor_id, date = data['patient_id'], data['doctor_id'], data['date']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date) VALUES (?, ?, ?)", 
                (patient_id, doctor_id, date))
    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment booked successfully!"}), 201

@appointments_bp.route('/list/<int:user_id>', methods=['GET'])
def list_appointments(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, patient_id, doctor_id, date, status FROM appointments
        WHERE patient_id = ? OR doctor_id = ?
    """, (user_id, user_id))
    appointments = cursor.fetchall()
    conn.close()

    return jsonify({"appointments": appointments})
