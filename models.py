from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(128), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    service_requests = db.relationship('ServiceRequest', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.relationship('Service', backref='service_professional', lazy=True, uselist=False)
    service_requests = db.relationship('ServiceRequest', backref='service_request_professional', lazy=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    category = db.Column(db.String(64), db.ForeignKey('category.name', name='fk_serviceprofessional_category'), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    experience = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transactions = db.relationship('Transaction', backref='service_professional', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    base_price = db.Column(db.Float)
    services = db.relationship('Service', backref='category', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', name='fk_service_category'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id', name='fk_service_serviceprofessional'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    area_pincode = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviews = db.relationship('Review', backref='service', lazy=True)
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_servicerequest_user'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id', name='fk_servicerequest_serviceprofessional'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id', name='fk_servicerequest_service'), nullable=False)
    appointment = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    status = db.Column(
        db.Enum('pending', 'approved', 'completed', 'canceled', name='service_request_status'),
        nullable=False,
        default='pending'
    )
    otp = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    transactions = db.relationship('Transaction', backref='service_request', lazy=True, uselist=False)
    payment_status = db.Column(
        db.Enum('pending', 'held', 'released', 'refunded', name='payment_status'),
        nullable=False,
        default='pending'
    )

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id', name='fk_review_service'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_review_user'), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_transaction_user'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id', name='fk_transaction_serviceprofessional'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id', name='fk_transaction_servicerequest'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('pending', 'completed', 'failed', 'refunded', name='transaction_status'),
        nullable=False,
        default='pending'
    )

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        passhash = generate_password_hash('admin')
        admin = User(username='admin', passhash=passhash, name='admin', email='admin@example.com')
        db.session.add(admin)
        db.session.commit()