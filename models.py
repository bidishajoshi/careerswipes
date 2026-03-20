from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # 'user' or 'company'
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    # Job Seeker specifics
    skills = db.Column(db.Text, nullable=True) # Comma-separated skills
    experience_level = db.Column(db.String(50), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    resume = db.Column(db.String(255), nullable=True) # File path for uploaded resume
    # Company specifics
    company_size = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    swipes = db.relationship('Swipe', backref='user', lazy=True)
    
class Job(db.Model):
    __tablename__ = 'job'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False) # Required skills, comma-separated
    
    # Relationships
    company = db.relationship('User', backref=db.backref('jobs', lazy=True))
    swipes = db.relationship('Swipe', backref='job', lazy=True)

class Swipe(db.Model):
    __tablename__ = 'swipe'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    liked = db.Column(db.Boolean, nullable=False) # True for right swipe, False for left swipe
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
