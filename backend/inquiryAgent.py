from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing
import datetime

class AppointmentInquirerAgent:
    def __init__(self):
        self.app = Flask(__name__)
        self.query = None
        self.intent = None
        self.entities = {}
        self.metadata = {}

        # API Endpoints
        self.app.route('/inquire_appointment', methods=['POST'])(self.inquire_appointment)
        self.app.route('/get_doctors', methods=['POST'])(self.get_doctors)
        self.app.route('/health', methods=['GET'])(self.health_check)

    def health_check(self):
        return jsonify({"status": "ok", "service": "inquirer-agent"})
    def inquire_appointment(self):
        """Fetch appointment details for a given name (can be a patient or a doctor)"""
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            self.query = data.get('query')
            self.intent = data.get('intent')
            self.entities = data.get('entities', {})
            self.metadata = data.get('metadata', {})

            name = self.entities.get('name')  # Extract only 'name' (can be patient or doctor)
            if not name:
                return jsonify({'response': "Please specify a name to check appointments."})

            with closing(sqlite3.connect('hospital.db')) as conn:
                conn.row_factory = sqlite3.Row  # This allows accessing columns by name
                c = conn.cursor()

                # Check if the name matches a patient
                c.execute("""
                    SELECT d.name as doctor_name, a.date, a.time, a.status 
                    FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE a.patient_name = ? 
                    ORDER BY a.date, a.time
                """, (name,))
                
                patient_appointments = c.fetchall()

                # Check if the name matches a doctor
                c.execute("""
                    SELECT a.patient_name, a.date, a.time, a.status 
                    FROM appointments a
                    WHERE a.doctor_id = (SELECT id FROM doctors WHERE name = ?)
                    ORDER BY a.date, a.time
                """, (name,))
                
                doctor_appointments = c.fetchall()

            response = ""

            # If name is a patient
            if patient_appointments:
                response += f"📋 **Appointments for patient {name}:**\n"
                for i, appt in enumerate(patient_appointments, 1):
                    status_emoji = {
                        'scheduled': '📅',
                        'completed': '✅',
                        'canceled': '❌'
                    }.get(appt['status'], '📝')

                    response += f"{i}. {status_emoji} With {appt['doctor_name']} on {appt['date']} at {appt['time']} (Status: {appt['status']})\n"

            # If name is a doctor
            if doctor_appointments:
                response += f"\n🩺 **Appointments for {name}:**\n"
                for i, appt in enumerate(doctor_appointments, 1):
                    status_emoji = {
                        'scheduled': '📅',
                        'completed': '✅',
                        'canceled': '❌'
                    }.get(appt['status'], '📝')

                    response += f"{i}. {status_emoji} Patient: {appt['patient_name']} on {appt['date']} at {appt['time']} (Status: {appt['status']})\n"

            # If no records found
            if not response:
                response = f"No appointments found for {name}."

            return jsonify({'response': response})

        except Exception as e:
            print(f"Error inquiring appointment: {str(e)}")
            return jsonify({'error': f"Failed to retrieve appointment details: {str(e)}"}), 500


    def get_doctors(self):
        """Fetch doctors based on the given specialty with their available appointment dates"""
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            self.query = data.get('query')
            self.intent = data.get('intent')
            self.entities = data.get('entities', {})
            self.metadata = data.get('metadata', {})
            
            specialty = self.entities.get('specialist_name')  # Get the specialist name
            if not specialty:
                return jsonify({'response': "Please provide a specialist (e.g., Cardiologist) to find relevant doctors."})
            
            with closing(sqlite3.connect('hospital.db')) as conn:
                conn.row_factory = sqlite3.Row  # This allows accessing columns by name
                c = conn.cursor()
                
                # Fetch doctors based on specialty
                c.execute("""
                    SELECT d.id, d.name, d.specialty 
                    FROM doctors d 
                    WHERE d.specialty = ?
                """, (specialty,))
                
                doctors = c.fetchall()
                
                if doctors:
                    response = f"Here are the available {specialty} doctors:\n\n"
                    
                    for doc in doctors:
                        doctor_id = doc['id']
                        doctor_name = doc['name']
                        
                        # Get the latest appointment for this doctor
                        c.execute("""
                            SELECT date, time 
                            FROM appointments 
                            WHERE doctor_id = ? AND status = 'scheduled' 
                            ORDER BY date ASC, time ASC
                            LIMIT 1
                        """, (doctor_id,))
                        
                        latest_appointment = c.fetchone()
                        
                        # Get next 3 available dates (assuming weekdays, not already booked)
                        today = datetime.date.today()
                        
                        # Get all booked dates/times for this doctor
                        c.execute("""
                            SELECT date, time 
                            FROM appointments 
                            WHERE doctor_id = ? AND status = 'scheduled'
                        """, (doctor_id,))
                        
                        booked_slots = set((row['date'], row['time']) for row in c.fetchall())
                        
                        # Generate next 3 available dates
                        available_dates = []
                        check_date = today
                        count = 0
                        
                        while count < 3:
                            # Skip weekends
                            if check_date.weekday() < 5:  # 0-4 are Monday to Friday
                                # Check morning and afternoon slots
                                for slot_time in ['09:00', '14:00']:
                                    date_str = check_date.strftime('%Y-%m-%d')
                                    if (date_str, slot_time) not in booked_slots:
                                        available_dates.append(f"{date_str} at {slot_time}")
                                        count += 1
                                        if count >= 3:
                                            break
                            
                            # Move to next day
                            check_date += datetime.timedelta(days=1)
                        
                        # Add doctor info and available dates to response
                        response += f"🩺 {doctor_name} ({doc['specialty']})\n"
                        
                        if latest_appointment:
                            response += f"   Next appointment: {latest_appointment['date']} at {latest_appointment['time']}\n"
                        else:
                            response += f"   No upcoming appointments scheduled\n"
                        
                        response += f"   Available slots:\n"
                        for date in available_dates:
                            response += f"   - {date}\n"
                        
                        response += "\n"
                else:
                    response = f"No available {specialty} doctors found."
                    
                return jsonify({'response': response})
                
        except Exception as e:
            print(f"Error retrieving doctor details: {str(e)}")
            return jsonify({'error': f"Failed to retrieve doctor details: {str(e)}"}), 500


if __name__ == '__main__':
    print("Starting Inquirer Agent on http://localhost:5002...")
    inquirer = AppointmentInquirerAgent()
    inquirer.app.run(port=5002, debug=True, threaded=True)
