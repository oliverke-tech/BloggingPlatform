from flask import Flask, request, jsonify

app = Flask(__name__)

# A simple in-memory database to store user data
users = {}
posts = []

@app.route("/")
def main():
    return "Welcome!"


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return jsonify({'message': 'Username already exists!'}), 400
    else:
        users[username] = password
        return jsonify({'message': 'Signup successful!'}), 201
    

@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(posts)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    post = {'title': title, 'content': content}
    posts.append(post)

    return jsonify({'message': 'Post created successfully!', 'post': post}), 201

if __name__ == '__main__':
    app.run(debug=True)