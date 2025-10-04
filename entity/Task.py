from datetime import datetime
from extensions import db
from enum import Enum

class StatusEnum(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # link to user
    created_at = db.Column(db.DateTime, default=datetime.now())
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False)