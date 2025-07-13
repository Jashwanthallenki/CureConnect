from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

# Store connections and room IDs
user_rooms = {}
user_roles = {}  # To store the role of the user (doctor or patient)

# Route to serve the main chat page
@app.route("/")
def index():
    return render_template("index.html")

# WebSocket event handler for user connections
@socketio.on('connect')
def handle_connect():
    print("A user connected!")

# WebSocket event for joining a room (doctor-patient chat room)
@socketio.on('join')
def on_join(data):
    username = data['username']
    role = data['role']
    room_id = data['room_id']
    
    user_rooms[username] = room_id  # Store the user and their room
    user_roles[username] = role  # Store the role of the user

    join_room(room_id)  # Join a specific room for the doctor-patient conversation
    print(f"{username} with role {role} joined room {room_id}")
    
    # Send welcome message to the user when they join
    emit('message', {'data': f"{username} has entered the room."}, room=room_id)

# WebSocket event for receiving and sending messages
@socketio.on('message')
def handle_message(data):
    room_id = data['room_id']
    message = data['message']
    username = data['username']
    role = user_roles.get(username, 'unknown')  # Get the role of the sender
    
    print(f"Message from {username} ({role}): {message}")
    
    # Send the message to the other user (doctor-patient chat)
    if role == 'Patient':
        # Send to the doctor
        emit('message', {'data': f"Patient ({username}): {message}"}, room=room_id)
    elif role == 'Doctor':
        # Send to the patient
        emit('message', {'data': f"Doctor ({username}): {message}"}, room=room_id)

# WebSocket event for disconnecting
@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected!")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5006)
