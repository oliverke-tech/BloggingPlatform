from flask import Flask, request, jsonify, make_response
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

users = {}
posts = {}
app.config['SECRET_KEY'] = 'your_secret_key'

def check_auth(username, password):
    return username in users and users[username]['password'] == password

def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        token_parts = token.split()

        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return 'Invalid token. Please provide a valid Bearer token.', None

        token = token_parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

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
    token = generate_token(username)
    return jsonify({'message': 'User created successfully!', 'username': username, 'token': token}), 201

@app.route('/signin', methods=['POST'])
def signin():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = generate_token(auth.username)
    return jsonify({'message': 'Login successful!', 'username': auth.username, 'token': token})

@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(list(posts.values()))

@app.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    post_id = len(posts) + 1
    post = {'id': post_id, 'title': title, 'content': content, 'author': current_user}
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
@token_required
def update_post(current_user, post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    post = posts[post_id]
    if post['author'] != current_user:
        return jsonify({'message': 'You are not authorized to update this post!'}), 403

    post['title'] = title if title else post['title']
    post['content'] = content if content else post['content']

    return jsonify({'message': 'Post updated successfully!', 'post': post})

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    if post_id not in posts:
        return jsonify({'message': 'Post not found!'}), 404

    post = posts[post_id]
    if post['author'] != current_user:
        return jsonify({'message': 'You are not authorized to delete this post!'}), 403

    del posts[post_id]
    return jsonify({'message': 'Post deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
