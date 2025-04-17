from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
from models.user import User, db
from chat_bot.chat_bot import chat_with_bot

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)
# Set session to be permanent and last for 7 days
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=2)
app.config["SESSION_PERMANENT"] = True

db.init_app(app)

with app.app_context():
    db.create_all()

def login_required(f):
    def decorated_function(*args, **kwargs):
        print(f"Checking session: {session}")
        if "user_id" not in session:
            print("No user_id in session")
            return jsonify({"error": "Please log in to access this resource."}), 401
        user = User.query.get(session["user_id"])
        if not user:
            print(f"User not found for session user_id: {session['user_id']}")
            session.pop("user_id", None)
            return jsonify({"error": "User not found. Please login again"}), 401
        print(f"User authenticated: {user.username}")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    required_fields = ["username", "password", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    
    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict()
    }), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401
    
    session["user_id"] = user.id
    return jsonify({
        "message": "Logged in successfully",
        "user": user.to_dict()
    })

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"})

@app.route("/me", methods=["GET"])
@login_required
def get_current_user():
    user = User.query.get(session["user_id"])
    return jsonify(user.to_dict())

@app.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route("/ping", methods=["GET"])
def ping():
    print("Ping received")
    return jsonify({"message": "pong"}), 200

# Route to chat with the AI bot
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    print(f"Session state in chat route: {session}")
    if "user_id" in session:
        print(f"User is logged in, ID: {session['user_id']}")
    else:
        print("No user logged in")
    data = request.get_json()
    print(f"Received data: {data}")
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400
    user_input = data["message"]
    print(f"Processing message: {user_input}")
    response_text = chat_with_bot(user_input)
    print(f"response: {response_text}")
    
    # Clean up the response if it contains agent thoughts
    if isinstance(response_text, str):
        if "Thought:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
        elif "Final Answer:" in response_text:
            response_text = response_text.split("Final Answer:")[-1].strip()
    
    if response_text:
        return jsonify({"response": response_text}), 200
    else:
        return jsonify({"error": "Empty response from bot"}), 500



if __name__ == "__main__":
    app.run(debug=True, port=4000, host="0.0.0.0")