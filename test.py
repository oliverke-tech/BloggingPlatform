from flask import Flask, request, jsonify, make_response
from functools import wraps
import base64

app = Flask(__name__)

# A simple in-memory database to store users and blog posts
users = {}
posts = {}

# Function to generate basic authentication token
def generate_auth_token(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return token

# Function to check if the provided username and password match
def check_auth(username, password):
    return username in users and users[username]['password'] == password

# Decorator function to require authentication for certain endpoints
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Unauthorized access!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    if username in users:
        return jsonify({'message': 'Username already exists!'}), 400

    users[username] = {'password': password}
    token = generate_auth_token(username, password)
    return jsonify({'message': 'User created successfully!', 'username': username, 'token': token}), 201

@app.route('/signin', methods=['POST'])
def signin():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = generate_auth_token(auth.username, auth.password)
    return jsonify({'message': 'Login successful!', 'username': auth.username, 'token': token})

@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(list(posts.values()))

@app.route('/posts', methods=['POST'])
@requires_auth
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    post_id = len(posts) + 1
    post = {'id': post_id, 'title': title, 'content': content, 'author': request.authorization.username}
    posts[post_id] = post

    return jsonify({'message': 'Post created successfully!', 'post': post}), 201

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = posts.get(post_id)
    if post:
        return jsonify(post)
    else:
        return jsonify({'message': 'Post not found!'}), 404

@app.route('/posts/<int:post_id>', methods=['PUT'])
@requires_auth
def update_post(post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    post = posts[post_id]
    if post['author'] != request.authorization.username:
        return jsonify({'message': 'You are not authorized to update this post!'}), 403

    post['title'] = title if title else post['title']
    post['content'] = content if content else post['content']

    return jsonify({'message': 'Post updated successfully!', 'post': post})

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@requires_auth
def delete_post(post_id):
    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    post = posts[post_id]
    if post['author'] != request.authorization.username:
        return jsonify({'message': 'You are not authorized to delete this post!'}), 403

    del posts[post_id]
    return jsonify({'message': 'Post deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
