from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_user_message = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref=db.backref("chat_messages", lazy=True))