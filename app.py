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

# Endpoints para CRUD de usuarios
@app.route('users', methods=['POST'])
@require_api_key
def create_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'], password=generate_password_hash(data['password'], method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'User created successfully'}), 201

@app.route('/users/<int:id>', methods=['PUT'])
@require_api_key
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'User not found'}), 404
    
    user.name = data['name']
    user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'], methods='sha256')
    db.session.commit()
    return jsonify({'message':'User updated successfully'}), 200

@app.route('/users/<int:id>', methods=['DELETE'])
@require_api_key
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'User deleted successfully'}), 200

# endpoint para CRUD pagamentos
@app.route('/payments', methods=['POST'])
@require_api_key
def create_payment():
    data = request.get_json()
    new_payment = Payment(user_id=data['user_id'], amount=data['amount'], status=data['status'])
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'message':'Payment created successfully'}), 201

@app.route('/payments/<int:id>', methods=['PUT'])
@require_api_key
def update_payment(id):
    data = request.get_json()
    payment = Payment.query.get(id)
    if not payment:
        return jsonify({'message':'Payment not found'}), 404
    
    payment.amount = data['amount']
    payment.status = data['status']
    db.session.commit()
    return jsonify({'message':'Payment nupdated successfully'}), 200

@app.route('/payments/<int:id>', methods=['DELETE'])
@require_api_key
def delete_payment(id):
    payment = Payment.query.get(id)
    if not payment:
        return jsonify({'message':'Payment not found'}), 404
    
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'message':'Payment deleted successfully'}), 200

# endpoints para CRUD Transacoes
@app.route('/transactions', methods=['POST'])
@require_api_key
def create_transaction():
    data = request.get_json()
    new_transaction = Transaction(payment_id=data['payment_id'], transaction_date=data['transaction_date'], transaction_type=data['transaction_type'] )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message':'Transaction created successfully'}), 201

@app.route('/transactions/<int:id>', methods=['PUT'])
@require_api_key
def update_transaction(id):
    data = request.get_json()
    transaction = Transaction.query.get(id)
    if not transaction@
        return jsonify({'message':'Transaction not found'}), 404
    
    transaction.transaction_date = data['transaction_date']
    transaction.transaction_type = data['transaction_type']
    db.session.commit()
    return jsonify({'message':'Transaction updated successfully'}), 200

@app.route('/transactions/<int:id>', methods=['DELETE'])
@require_api_key
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if not transaction:
        return jsonify({'message':'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message':'Transaction deleted successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)