from flask import Flask, request, jsonify
import base64
from app import model, db, app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import jwt
import json

users = {}
posts = {}
app.config['SECRET_KEY'] = 'your_secret_key'

with app.app_context():
    db.create_all()

# Function to generate JWT token
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Decorator function to enforce token requirement for certain routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        token_parts = token.split()

        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return 'Invalid token. Please provide a valid Bearer token.', None

        token = token_parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 400

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 400

        return f(current_user, *args, **kwargs)

    return decorated


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
        token = generate_token(username)
        return jsonify({'message': 'Login successful!', 'username': username, 'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password!'}), 400


@app.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    # Create a new post instance
    new_post = model.Post(title=title, content=content, author=current_user)

    # Add the post to the database session
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully!'}), 201


@app.route('/posts', methods=['GET'])
def get_posts():
    # Query all posts from the database
    posts = model.Post.query.all()

    # Convert SQLAlchemy objects to dictionary representation
    posts_data = [{'id': post.id, 'author': post.author, 'title': post.title, 'content': post.content} for post in posts]

    return jsonify(posts_data), 200


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    # Query the post from the database
    post = model.Post.query.get(post_id)

    if post:
        # Convert the post object to a dictionary representation
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author
        }
        return jsonify(post_data), 200
    else:
        return jsonify({'message': 'Post not found!'}), 400


@app.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    # Query the post from the database
    post = model.Post.query.get(post_id)

    # Check if the post exists
    if not post:
        return jsonify({'message': 'Post not found!'}), 400

    # Check if the current user is the author of the post
    if post.author != current_user:
        return jsonify({'message': 'You are not authorized to update this post!'}), 400

    # Update the post attributes
    post.title = title
    post.content = content

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Post updated successfully!'}), 200


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    # Query the post from the database
    post = model.Post.query.get(post_id)

    # Check if the post exists
    if not post:
        return jsonify({'message': 'Post not found!'}), 400

    # Check if the current user is the author of the post
    if post.author != current_user:
        return jsonify({'message': 'You are not authorized to delete this post!'}), 400

    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted successfully!'}), 200


if __name__ == '__main__':
    app.run(debug=True)
