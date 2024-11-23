from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)  
    email = db.Column(db.String(128), unique=True, nullable=True)
    service_requests = db.relationship('ServiceRequest', backref='user', lazy=True) 
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.relationship('Service', backref='service_professional', lazy=True)
    service_requests = db.relationship('ServiceRequest', backref='service_professional', lazy=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    category = db.Column(db.String(64), db.ForeignKey('category.name'), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    experience = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    transactions = db.relationship('Transaction', backref='service_professional', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    services = db.relationship('Service', backref='category', lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    price = db.Column(db.Float, nullable=False)  
    time = db.Column(db.Integer, nullable=False)  
    reviews = db.relationship('Review', backref='service', lazy=True)
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    appointment = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum('pending', 'approved', 'completed', 'canceled', name='service_request_status'),
        nullable=False,
        default='pending'
    )
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    payment_status = db.Column(
        db.Enum('pending', 'held', 'released', 'refunded', name='payment_status'),
        nullable=False,
        default='pending'
    )

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('pending', 'completed', 'failed', 'refunded', name='transaction_status'),
        nullable=False,
        default='pending'
    )

with app.app_context():
    db.create_all()
