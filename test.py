from flask import Flask, request, jsonify, make_response
import jwt
import datetime
from functools import wraps
import pymysql

app = Flask(__name__)

users = {}
posts = {}
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ke981015'
app.config['MYSQL_DB'] = 'blog_platform'

mysql = pymysql.connect(host=app.config['MYSQL_HOST'],
                        user=app.config['MYSQL_USER'],
                        passwd=app.config['MYSQL_PASSWORD'],
                        db=app.config['MYSQL_DB'])

cursor = mysql.cursor()

# create_users_table_sql = """
# CREATE TABLE IF NOT EXISTS users (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(255) UNIQUE NOT NULL,
#     password VARCHAR(255) NOT NULL
# )
# """

# cursor.execute(create_users_table_sql)

# mysql.commit()

def check_auth(username, password):
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    return user is not None

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
            return jsonify({'message': 'Token is missing!'}), 400

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 400

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    # if username in users:
    #     return jsonify({'message': 'Username already exists!'}), 400

    # users[username] = {'password': password}
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({'message': 'Username already exists!'}), 400

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.commit()

    token = generate_token(username)
    return jsonify({'message': 'User created successfully!', 'username': username, 'token': token}), 200

@app.route('/signin', methods=['POST'])
def signin():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({'message': 'Invalid username or password!'}), 400

    token = generate_token(auth.username)
    return jsonify({'message': 'Login successful!', 'username': auth.username, 'token': token})

@app.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    # post_id = len(posts) + 1
    # post = {'id': post_id, 'title': title, 'content': content, 'author': current_user}
    # posts[post_id] = post
    cursor.execute("INSERT INTO posts (title, content, author) VALUES (%s, %s, %s)", (title, content, current_user))
    mysql.commit()

    return jsonify({'message': 'Post created successfully!'}), 200

@app.route('/posts', methods=['GET'])
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return jsonify(posts)

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    if post:
        return jsonify(post)
    else:
        return jsonify({'message': 'Post not found!'}), 400

@app.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    if not post:
        return jsonify({'message': 'Post not found!'}), 400

    if post[3] != current_user:
        return jsonify({'message': 'You are not authorized to update this post!'}), 400

    cursor.execute("UPDATE posts SET title=%s, content=%s WHERE id=%s", (title, content, post_id))
    mysql.commit()

    return jsonify({'message': 'Post updated successfully!'})

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    if not post:
        return jsonify({'message': 'Post not found!'}), 400

    if post[3] != current_user:
        return jsonify({'message': 'You are not authorized to delete this post!'}), 400

    cursor.execute("DELETE FROM posts WHERE id=%s", (post_id,))
    mysql.commit()

    return jsonify({'message': 'Post deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)