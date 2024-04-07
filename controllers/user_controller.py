from flask import request, jsonify
from models import User

def register_user():
    data = request.get_json()
    if 'name' not in data or 'password' not in data:
        return jsonify({'message': 'Name and password are required!'}), 400
    
    user = User(data['name'], data['password'])
    user_collection = db['users']
    user_collection.insert_one({'public_id': user.public_id, 'name': user.name, 'password_hash': user.password_hash})
    
    return jsonify({'public_id': user.public_id, 'message': 'User created successfully!'})
