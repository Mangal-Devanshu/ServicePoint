from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True) 
    username = db.Column(db.String[32] , unique=True)
    passhash = db.Column(db.String[256], nullable =False)
    name = db.Column(db.String[64], nullable =True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(32), nullable=False)

    carts = db.relationship('Cart', backref='user', lazy=True)
    transaction_id = db.relationship('Transaction' , backref='user' ,lazy =True)

class Category(db.Model):
    id = db.Column(db.Integer , primary_key =True)
    name = db.Column(db.String[64] ,nullable=False , unique=True)
    services = db.relationship('Service' , backref='category' , lazy=True)


cart_service = db.Table('cart_service',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)

class Service(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    category_id = db.Column(db.Integer , db.ForeignKey('category.id'),nullable = False)
    name = db.Column(db.String[64],nullable=False)
    description = db.Column(db.String[256] , nullable = True)
    price = db.Column(db.Float , nullable =False)
    review = db.relationship('Review', backref='service' , lazy=True)
    carts = db.relationship('Cart', secondary=cart_service, backref='services', lazy='dynamic')

class Review(db.Model):
    id= db.Column(db.Integer , primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'),nullable =False)
    description = db.Column(db.String[256],nullable=False) 

class Cart(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'),nullable =False)
    services = db.relationship('Service', secondary=cart_service, backref='carts', lazy='dynamic')

class Transaction(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'), nullable=False)
    cart_id = db.Column(db.Integer , db.ForeignKey('cart.id'), nullable=False)
    price = db.Column(db.Float , nullable =False)
    date = db.Column(db.Date , nullable=False)
    status = db.Column(db.String(64), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

with app.app_context():
    db.create_all()
