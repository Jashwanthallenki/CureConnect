from flask import Blueprint, request, jsonify
import sqlite3
from flask_cors import CORS  # Import CORS

auth_bp = Blueprint("auth", __name__)

# Apply CORS to allow frontend (5500) to talk to backend (5000)
CORS(auth_bp)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name, email, password, phone, location, role = (
        data['name'], data['email'], data['password'],
        data['phone'], data['location'], data['role']
    )

    try:
        conn = sqlite3.connect("cureconnect.db")  # ✅ Use your DB file
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, location, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, password, phone, location, role))
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data['email'], data['password']

    conn = sqlite3.connect("cureconnect.db")
    cursor = conn.cursor()

    # Fetch user from DB
    cursor.execute("SELECT id, name, password, role FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    
    if user:
        user_id, name, stored_password, role = user
        print(f"Stored Password in DB: {stored_password}")
        print(f"Entered Password: {password}")

        if password == stored_password:  # Direct comparison since no hashing
            return jsonify({"message": "Login successful!", "user_id": user_id, "name": name, "role": role})
        else:
            return jsonify({"error": "Invalid password"}), 401
    else:
        return jsonify({"error": "Invalid email"}), 401

