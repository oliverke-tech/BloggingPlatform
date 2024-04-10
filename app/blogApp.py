from flask import Flask, request, jsonify
import base64
from app import model, db, app
from werkzeug.security import generate_password_hash, check_password_hash
import json

users = {}
posts = {}

with app.app_context():
    db.create_all()

def generate_auth_token(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return token


# Test Curl: curl localhost:5050/signup -X POST -d '{"username":"1234", "password":"5678"}' -H 'Content-Type: application/json'
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not in JSON format'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    # Check if the username already exists in the database
    existing_user = model.User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists!'}), 400

    # Hash the password before storing it in the database
    hashed_password = generate_password_hash(password)

    # Create a new user instance and add it to the database
    new_user = model.User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!', 'username': username}), 200


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not in JSON format'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    # Retrieve the user from the database
    user = model.User.query.filter_by(username=username).first()

    # Check if the user exists and verify the password
    if user and check_password_hash(user.password, password):
        # Generate token for authentication
        token = generate_auth_token(username, password)
        return jsonify({'message': 'Login successful!', 'username': username, 'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password!'}), 400
    

@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(list(posts.values()))


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = posts.get(post_id)
    if post:
        return jsonify(post)
    else:
        return jsonify({'message': 'Post not found!'}), 404


@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    title = data.get('title')
    content = data.get('content')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    if username not in users or users[username]['password'] != password:
        return jsonify({'message': 'Invalid username or password!'}), 401

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    post_id = len(posts) + 1
    post = {'id': post_id, 'title': title, 'content': content, 'author': username}
    posts[post_id] = post

    return jsonify({'message': 'Post created successfully!', 'post': post}), 201


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    del posts[post_id]
    return jsonify({'message': 'Post deleted successfully!'})


@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    post = posts[post_id]
    post['title'] = title if title else post['title']
    post['content'] = content if content else post['content']

    return jsonify({'message': 'Post updated successfully!', 'post': post})


if __name__ == '__main__':
    app.run(debug=True)
