from flask import Flask
from routes.auth import auth_bp
from routes.appointments import appointments_bp
from routes.chat import chat_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(appointments_bp, url_prefix='/appointments')
app.register_blueprint(chat_bp, url_prefix='/chat')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
