from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing
from agent_db import init_db
from flask_cors import CORS  # Import CORS

class AppointmentSchedulerAgent:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})  # Allow all origins (restrict in production)

        self.query = None
        self.intent = None
        self.entities = {}
        self.metadata = {}

        self.app.route('/schedule_appointment', methods=['POST'])(self.schedule_appointment)
        self.app.route('/reschedule_appointment', methods=['POST'])(self.reschedule_appointment)
        self.app.route('/cancel_appointment', methods=['POST'])(self.cancel_appointment)
        self.app.route('/health', methods=['GET'])(self.health_check)

    def health_check(self):
        return jsonify({"status": "ok", "service": "scheduler-agent"})

    def schedule_appointment(self):
        try:
            data = request.json
            print(data)
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            self.query = data.get('query')
            self.intent = data.get('intent')
            self.entities = data.get('entities', {})
            self.metadata = data.get('metadata', {})

            patient_name = self.entities.get('patient_name')
            doctor_name = self.entities.get('doctor_name')
            date = self.entities.get('date')
            time = self.entities.get('time')

            missing_fields = []
            if not patient_name:
                missing_fields.append("patient name")
            if not doctor_name:
                missing_fields.append("doctor name")
            if not date:
                missing_fields.append("date")
            if not time:
                missing_fields.append("time")

            if missing_fields:
                return jsonify({
                    'response': f"I need more information to schedule the appointment. Missing: {', '.join(missing_fields)}"
                })

            with closing(sqlite3.connect('hospital.db')) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign key constraints
                c = conn.cursor()
                
                # First, get the doctor's ID from the name
                c.execute("SELECT id FROM doctors WHERE name = ?", (doctor_name,))
                doctor_result = c.fetchone()
                
                if not doctor_result:
                    return jsonify({
                        'response': f"I couldn't find {doctor_name} in our system. Please check the name and try again."
                    })
                    
                doctor_id = doctor_result[0]
                
                # Check if doctor is already booked at that time
                c.execute("""
                    SELECT COUNT(*) FROM appointments 
                    WHERE doctor_id = ? AND date = ? AND time = ? AND status = 'scheduled'
                """, (doctor_id, date, time))
                
                doctor_booked = c.fetchone()[0] > 0
                
                if doctor_booked:
                    return jsonify({
                        'response': f"{doctor_name} is already booked at {time} on {date}. Please choose another time."
                    })
                    
                # Check if patient already has an appointment with the same doctor on the same date
                c.execute("""
                    SELECT COUNT(*) FROM appointments 
                    WHERE patient_name = ? AND doctor_id = ? AND date = ? AND status = 'scheduled'
                """, (patient_name, doctor_id, date))
                
                patient_has_appointment = c.fetchone()[0] > 0
                
                if patient_has_appointment:
                    return jsonify({
                        'response': f"{patient_name} already has an appointment with {doctor_name} on {date}. Would you like to reschedule instead?"
                    })
                    
                # Check if patient has appointments with other doctors at the same time
                c.execute("""
                    SELECT d.name FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE a.patient_name = ? AND a.date = ? AND a.time = ? AND a.status = 'scheduled'
                """, (patient_name, date, time))
                
                conflicting_doctor = c.fetchone()
                
                if conflicting_doctor:
                    return jsonify({
                        'response': f"{patient_name} already has an appointment with {conflicting_doctor[0]} at {time} on {date}. Please choose another time."
                    })

                # All checks passed, insert the appointment with the default 'scheduled' status
                c.execute("""
                    INSERT INTO appointments (patient_name, doctor_id, date, time, status) 
                    VALUES (?, ?, ?, ?, 'scheduled')
                """, (patient_name, doctor_id, date, time))
                conn.commit()

            return jsonify({
                'response': f"Great! I've scheduled an appointment for {patient_name} with {doctor_name} on {date} at {time}."
            })

        except sqlite3.Error as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({'error': f"Database error: {str(db_error)}"}), 500

        except Exception as e:
            print(f"Error scheduling appointment: {str(e)}")
            return jsonify({'error': f"Failed to schedule appointment: {str(e)}"}), 500

    def reschedule_appointment(self):
        """Reschedule an existing appointment to a new date/time"""
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            self.query = data.get('query')
            self.intent = data.get('intent')
            self.entities = data.get('entities', {})
            self.metadata = data.get('metadata', {})

            patient_name = self.entities.get('patient_name')
            doctor_name = self.entities.get('doctor_name')
            current_date = self.entities.get('current_date')
            current_time = self.entities.get('current_time')
            new_date = self.entities.get('new_date')
            new_time = self.entities.get('new_time')

            missing_fields = []
            if not patient_name:
                missing_fields.append("patient name")
            if not doctor_name:
                missing_fields.append("doctor name")
            if not current_date:
                missing_fields.append("current appointment date")
            if not current_time:
                missing_fields.append("current appointment time")
            if not new_date:
                missing_fields.append("new appointment date")
            if not new_time:
                missing_fields.append("new appointment time")

            if missing_fields:
                return jsonify({
                    'response': f"I need more information to reschedule the appointment. Missing: {', '.join(missing_fields)}"
                })

            with closing(sqlite3.connect('hospital.db')) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                c = conn.cursor()
                
                # Get the doctor's ID
                c.execute("SELECT id FROM doctors WHERE name = ?", (doctor_name,))
                doctor_result = c.fetchone()
                
                if not doctor_result:
                    return jsonify({
                        'response': f"I couldn't find {doctor_name} in our system. Please check the name and try again."
                    })
                
                doctor_id = doctor_result[0]
                
                # Find the existing appointment
                c.execute("""
                    SELECT id FROM appointments 
                    WHERE patient_name = ? AND doctor_id = ? AND date = ? AND time = ? AND status = 'scheduled'
                """, (patient_name, doctor_id, current_date, current_time))
                
                appointment = c.fetchone()
                
                if not appointment:
                    return jsonify({
                        'response': f"I couldn't find an existing appointment for {patient_name} with {doctor_name} on {current_date} at {current_time}."
                    })
                
                appointment_id = appointment[0]
                
                # Check if the new time slot is available
                c.execute("""
                    SELECT COUNT(*) FROM appointments 
                    WHERE doctor_id = ? AND date = ? AND time = ? AND status = 'scheduled' AND id != ?
                """, (doctor_id, new_date, new_time, appointment_id))
                
                doctor_booked = c.fetchone()[0] > 0
                
                if doctor_booked:
                    return jsonify({
                        'response': f"{doctor_name} is already booked at {new_time} on {new_date}. Please choose another time."
                    })
                
                # Check if patient has other appointments at the same time
                c.execute("""
                    SELECT d.name FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE a.patient_name = ? AND a.date = ? AND a.time = ? AND a.status = 'scheduled' AND a.id != ?
                """, (patient_name, new_date, new_time, appointment_id))
                
                conflicting_doctor = c.fetchone()
                
                if conflicting_doctor:
                    return jsonify({
                        'response': f"{patient_name} already has an appointment with {conflicting_doctor[0]} at {new_time} on {new_date}. Please choose another time."
                    })
                
                # Update the appointment
                c.execute("""
                    UPDATE appointments 
                    SET date = ?, time = ? 
                    WHERE id = ?
                """, (new_date, new_time, appointment_id))
                
                conn.commit()
                
                return jsonify({
                    'response': f"Success! I've rescheduled {patient_name}'s appointment with {doctor_name} from {current_date} at {current_time} to {new_date} at {new_time}."
                })

        except sqlite3.Error as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({'error': f"Database error: {str(db_error)}"}), 500
            
        except Exception as e:
            print(f"Error rescheduling appointment: {str(e)}")
            return jsonify({'error': f"Failed to reschedule appointment: {str(e)}"}), 500

    def cancel_appointment(self):
        """Cancel an existing appointment by changing its status to 'canceled'"""
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            self.query = data.get('query')
            self.intent = data.get('intent')
            self.entities = data.get('entities', {})
            self.metadata = data.get('metadata', {})

            patient_name = self.entities.get('patient_name')
            doctor_name = self.entities.get('doctor_name')
            date = self.entities.get('date')
            time = self.entities.get('time')

            missing_fields = []
            if not patient_name:
                missing_fields.append("patient name")
            if not doctor_name:
                missing_fields.append("doctor name")
            if not date:
                missing_fields.append("appointment date")
            if not time:
                missing_fields.append("appointment time")

            if missing_fields:
                return jsonify({
                    'response': f"I need more information to cancel the appointment. Missing: {', '.join(missing_fields)}"
                })

            with closing(sqlite3.connect('hospital.db')) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                c = conn.cursor()
                
                # Get the doctor's ID
                c.execute("SELECT id FROM doctors WHERE name = ?", (doctor_name,))
                doctor_result = c.fetchone()
                
                if not doctor_result:
                    return jsonify({
                        'response': f"I couldn't find {doctor_name} in our system. Please check the name and try again."
                    })
                
                doctor_id = doctor_result[0]
                
                # Find the existing appointment
                c.execute("""
                    SELECT id FROM appointments 
                    WHERE patient_name = ? AND doctor_id = ? AND date = ? AND time = ? AND status = 'scheduled'
                """, (patient_name, doctor_id, date, time))
                
                appointment = c.fetchone()
                
                if not appointment:
                    return jsonify({
                        'response': f"I couldn't find an active appointment for {patient_name} with {doctor_name} on {date} at {time}."
                    })
                
                appointment_id = appointment[0]
                
                # Update the appointment status to 'canceled'
                c.execute("""
                    UPDATE appointments 
                    SET status = 'canceled' 
                    WHERE id = ?
                """, (appointment_id,))
                
                conn.commit()
                
                return jsonify({
                    'response': f"I've canceled {patient_name}'s appointment with {doctor_name} on {date} at {time}. The slot is now available for others."
                })

        except sqlite3.Error as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({'error': f"Database error: {str(db_error)}"}), 500
            
        except Exception as e:
            print(f"Error canceling appointment: {str(e)}")
            return jsonify({'error': f"Failed to cancel appointment: {str(e)}"}), 500


if __name__ == '__main__':
    print("Starting Scheduler Agent on http://localhost:5001...")
    init_db()  # Initialize the database
    scheduler = AppointmentSchedulerAgent()
    scheduler.app.run(port=5001, debug=True, threaded=True)