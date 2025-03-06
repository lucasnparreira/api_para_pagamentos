import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///payments.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(36), unique=True, nullable=False)
    api_key_expiration = db.Column(db.DateTime, nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeingKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)

def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.hearders.get('x-api-key')
        user = User.query.filter_by(api_key=api_key).first()
        if not api_key or not user or user.api_key_expiration < datatime.utcnow():
            return jsonify({'message': 'Invalid or expired API Key'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(name=data['name'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message':'Invalid credentials'}), 401
    
    user.api_key = str(uuid.uuid4())
    user.api_key_expiration = datetime.utcnow() + timedelta(minutes=5) # chave valida por 5 min
    db.session.commit()
    return jsonify({'api_key': user.api_key}), 200

@app.route('/logout', methods=['POST'])
def logout_user():
    api_key = request.headers.get('x-api-key')
    user = User.query.filter_by(api_key=api_key).first()
    if user:
        user.api_key = None 
        user.api_key_expiration = None 
        db.session.commit()
    return jsonify({'message':'Logged out successfully'}), 200

