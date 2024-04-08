from flask import Flask, request, jsonify

app = Flask(__name__)

users = {}
posts = {}

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    if username in users:
        return jsonify({'message': 'Username already exists!'}), 400

    users[username] = {'password': password}
    return jsonify({'message': 'User created successfully!', 'username': username}), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(list(posts.values()))

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

if __name__ == '__main__':
    app.run(debug=True)
