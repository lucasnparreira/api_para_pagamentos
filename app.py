import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(36), unique=True, nullable=False)
    api_key_expiration = db.Column(db.DateTime, nullable=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cash_account = db.Column(db.Float, nullable=False, default=0.0)
    date_open_account = db.Column(db.DateTime, nullable=False, default=datetime.now)

def require_api_key(f):
    @functools.wraps(f)  # Isso evita a sobrescrita do nome da função
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        user = User.query.filter_by(api_key=api_key).first()
        if not api_key or not user or user.api_key_expiration < datetime.utcnow():
            return jsonify({'message': 'Invalid or expired API Key'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    api_key = str(uuid.uuid4())
    api_key_expiration = datetime.utcnow() + timedelta(minutes=5)
    new_user = User(
        name=data['name'], 
        email=data['email'], 
        password=hashed_password, 
        api_key=api_key,
        api_key_expiration=api_key_expiration
    )

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
# endpoint removido pois o usuario ja é criado ao ser registrado no endpoint register
# @app.route('/users', methods=['POST'])
# @require_api_key
# def create_user():
#     data = request.get_json()
#     new_user = User(name=data['name'], email=data['email'], password=generate_password_hash(data['password'], method='pbkdf2:sha256'))
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({'message':'User created successfully'}), 201

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
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
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

@app.route('/users', methods=['GET'])
@require_api_key
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            'id':user.id,
            'name':user.name,
            'email':user.email,
            'api_key':user.api_key,
            'api_key_expiration':user.api_key_expiration
        })
    return jsonify(users_list), 200

@app.route('/users/<int:id>', methods=['GET'])
@require_api_key
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'User not found'}), 404
    
    return jsonify({
        'id':user.id,
            'name':user.name,
            'email':user.email,
            'api_key':user.api_key,
            'api_key_expiration':user.api_key_expiration
    }), 200

# CRUD para contas
@app.route('/account', methods=['POST'])
@require_api_key
def create_account():
    data = request.get_json()
    
    if 'user_id' not in data:
        return jsonify({'error':'user_id is required'}), 400
    
    new_account = Account(
        user_id=data['user_id'],
        cash_account=data.get('cash_account', 0.0),
        date_open_account=datetime.now()
        )
    
    db.session.add(new_account)
    db.session.commit()

    return jsonify({'message':'Account created successfully'}), 201

@app.route('/account/<int:id>', methods=['PUT'])
@require_api_key
def update_account(id):
    data = request.get_json()
    account = Account.query.get(id)
    if not account:
        return jsonify({'message':'Account not found'}), 404
    
    if 'user_id' in data:
        account.user_id = data['user_id']
    
    if 'cash_account' in data:
        account.cash_account = data['cash_account']

    db.session.commit()

    return jsonify({'message':'Account updated successfully'}), 200

@app.route('/account/<int:id>', methods=['DELETE'])
@require_api_key
def delete_account(id):
    account = Account.query.get(id)

    if not account:
        return jsonify({'message':'Account not found'}), 404
    
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message':'Account deleted successfully'}), 200

@app.route('/accounts', methods=['GET'])
@require_api_key
def get_accounts():
    accounts = Account.query.join(User, Account.user_id == User.id).add_columns(
        Account.id, Account.user_id, User.name, Account.cash_account, Account.date_open_account   
    ).all()
    accounts_list = []
    for account in accounts:
        accounts_list.append({
            'id':account.id,
            'user_id':account.user_id,
            'name':account.name,
            'cash_account':account.cash_account,
            'date_open_account':account.date_open_account
        })
    return jsonify(accounts_list), 200
    
@app.route('/account/<int:id>', methods=['GET'])
@require_api_key
def get_account(id):
    account = Account.query.get(id)
    if not account:
        return jsonify({'message':'Account not found'}), 404
    
    return jsonify({
        'id':account.id,
        'user_id':account.user_id,
        'cash_account':account.cash_account,
        'date_open_account':account.date_open_account
    }), 200

# endpoint para CRUD pagamentos
@app.route('/payments', methods=['POST'])
@require_api_key
def create_payment():
    data = request.get_json()

    payments = data if isinstance(data, list) else [data]

    for payment_data in payments:
        account = Account.query.get(payment_data['user_id'])

        if not account:
            return jsonify({'error':f"Account not found for user_id {payment_data['user_id']}"}), 404

        if payment_data['status'] == 'Credit':
            account.cash_account += payment_data['amount']
        
        else:
            if account.cash_account >= payment_data['amount']:
                account.cash_account -= payment_data['amount']
            else:
                return jsonify({'error':'Insuficient funds'}), 400
        
        new_payment = Payment(
            user_id = payment_data['user_id'],
            amount=payment_data['amount'],
            status=payment_data['status']
        )
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
    return jsonify({'message':'Payment updated successfully'}), 200

@app.route('/payments/<int:id>', methods=['DELETE'])
@require_api_key
def delete_payment(id):
    payment = Payment.query.get(id)
    if not payment:
        return jsonify({'message':'Payment not found'}), 404
    
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'message':'Payment deleted successfully'}), 200

@app.route('/payments', methods=['GET'])
@require_api_key
def get_payments():
    payments = Payment.query.all()  # Obtém todos os pagamentos
    payments_list = []
    for payment in payments:
        payments_list.append({
            'id': payment.id,
            'user_id': payment.user_id,
            'amount': payment.amount,
            'status': payment.status
        })
    return jsonify(payments_list), 200

@app.route('/payments/<int:id>', methods=['GET'])
@require_api_key
def get_payment(id):
    payment = Payment.query.get(id)  # Obtém o pagamento pelo ID
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404
    
    return jsonify({
        'id': payment.id,
        'user_id': payment.user_id,
        'amount': payment.amount,
        'status': payment.status
    }), 200

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
    if not transaction:
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

@app.route('/transactions', methods=['GET'])
@require_api_key
def get_transactions():
    transactions = Transaction.query.all()  # Obtém todas as transações
    transactions_list = []
    for transaction in transactions:
        transactions_list.append({
            'id': transaction.id,
            'payment_id': transaction.payment_id,
            'transaction_date': transaction.transaction_date,
            'transaction_type': transaction.transaction_type
        })
    return jsonify(transactions_list), 200

@app.route('/transactions/<int:id>', methods=['GET'])
@require_api_key
def get_transaction(id):
    transaction = Transaction.query.get(id)  # Obtém a transação pelo ID
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    return jsonify({
        'id': transaction.id,
        'payment_id': transaction.payment_id,
        'transaction_date': transaction.transaction_date,
        'transaction_type': transaction.transaction_type
    }), 200

if __name__ == '__main__':
    #db.create_all()
    with app.app_context():
        db.create_all()
    app.run(debug=True)