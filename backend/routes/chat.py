from flask import Blueprint, request, jsonify
import sqlite3
from models import DB_NAME

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.json
    sender_id, receiver_id, message = data['sender_id'], data['receiver_id'], data['message']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat (sender_id, receiver_id, message) VALUES (?, ?, ?)", 
                (sender_id, receiver_id, message))
    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent!"}), 201

@chat_bp.route('/history/<int:user_id>/<int:contact_id>', methods=['GET'])
def chat_history(user_id, contact_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_id, receiver_id, message, timestamp FROM chat
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (user_id, contact_id, contact_id, user_id))
    messages = cursor.fetchall()
    conn.close()

    return jsonify({"messages": messages})
