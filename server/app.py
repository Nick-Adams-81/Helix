from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
from models.user import User, ChatMessage, db
from chat_bot.chat_bot import chat_with_bot

app = Flask(__name__)

# Configure session
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Set session lifetime to 7 days
app.config['SESSION_PERMANENT'] = True

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Allows alchemy to create all db tables
with app.app_context():
    db.create_all()

# Function to ensure only logged in users can access certain routes by decorating the route 
# with the name of the function
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

# Signup route
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

# Login route
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

# Logout route
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"})

# Checking to make sure the loggedin user gets their data back
@app.route("/me", methods=["GET"])
@login_required
def get_current_user():
    user = User.query.get(session["user_id"])
    return jsonify(user.to_dict())

# Route to get single user by id
@app.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Route to chat with the AI bot
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    if "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        response = chat_with_bot(data["message"])
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Failed to process chat message"}), 500

@app.route("/test-chat", methods=["POST"])
def test_chat():
    try:
        new_message = ChatMessage(
            user_id = session["user_id"],
            message_text = "This is a test message",
            is_user_message=True
        )
        db.session.add(new_message)
        db.session.commit()

        messages = ChatMessage.query.filter_by(user_id=session["user_id"]).all()

        return jsonify({
            "success": True,
            "message": "Test message created",
            "messages": [{
                "id": msg.id,
                "text": msg.message_text,
                "is_user": msg.is_user_message,
                "created_at": msg.created_at.isformat()
            } for msg in messages]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=4000, host="0.0.0.0")