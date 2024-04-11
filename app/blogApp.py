from flask import Flask, request, jsonify
from app import model, db, app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import jwt
from http import HTTPStatus

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
            return jsonify({'message': 'Token is missing!'}), HTTPStatus.BAD_REQUEST

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), HTTPStatus.BAD_REQUEST

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user.

    This route allows users to register by providing a unique username and password.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the request body is missing or not in JSON format.
        BadRequest: If the username or password is missing.
        BadRequest: If the username already exists in the database.

    Examples:
        A sample successful response:
        {
            'message': 'User created successfully!',
            'username': 'example_user'
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not in JSON format'}), HTTPStatus.BAD_REQUEST

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), HTTPStatus.BAD_REQUEST

    # Check if the username already exists in the database
    existing_user = model.User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists!'}), HTTPStatus.BAD_REQUEST

    # Hash the password before storing it in the database
    hashed_password = generate_password_hash(password)

    # Create a new user instance and add it to the database
    new_user = model.User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!', 'username': username}), HTTPStatus.OK


@app.route('/signin', methods=['POST'])
def signin():
    """
    Log in a user.

    This route allows users to authenticate by providing their username and password.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the request body is missing or not in JSON format.
        BadRequest: If the username or password is missing.
        BadRequest: If the provided username or password is incorrect.

    Examples:
        A sample successful response:
        {
            'message': 'Login successful!',
            'username': 'example_user',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImV4YW1wbGVfdXNlciIsImlhdCI6MTYzMjg4OTM2MCwiZXhwIjoxNjMyODkwMjYwfQ.oh_SLCAlfQHGS8Pw1vm_cVMT23pYn6eIlMZIrYqQI-c'
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not in JSON format'}), HTTPStatus.BAD_REQUEST

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), HTTPStatus.BAD_REQUEST

    # Retrieve the user from the database
    user = model.User.query.filter_by(username=username).first()

    # Check if the user exists and verify the password
    if user and check_password_hash(user.password, password):
        # Generate token for authentication
        token = generate_token(username)
        return jsonify({'message': 'Login successful!', 'username': username, 'token': token}), HTTPStatus.OK
    else:
        return jsonify({'message': 'Invalid username or password!'}), HTTPStatus.BAD_REQUEST


@app.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    """
    Create a new post.

    This route allows authenticated users to create a new post by providing a title and content.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the request body is missing or not in JSON format.
        BadRequest: If the title or content of the post is missing.

    Examples:
        A sample successful response:
        {
            'message': 'Post created successfully!'
        }
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), HTTPStatus.BAD_REQUEST

    # Create a new post instance
    new_post = model.Post(title=title, content=content, author=current_user)

    # Add the post to the database session
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully!'}), HTTPStatus.OK


@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all posts.

    This route allows users to retrieve all posts available in the database.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Examples:
        A sample successful response:
        [
            {
                'id': 1,
                'author': 'John Doe',
                'title': 'First Post',
                'content': 'This is the content of the first post.'
            },
            {
                'id': 2,
                'author': 'Jane Smith',
                'title': 'Second Post',
                'content': 'This is the content of the second post.'
            }
        ]
    """
    # Query all posts from the database
    posts = model.Post.query.all()

    # Convert SQLAlchemy objects to dictionary representation
    posts_data = [{'id': post.id, 'author': post.author, 'title': post.title, 'content': post.content} for post in posts]

    return jsonify(posts_data), HTTPStatus.OK


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Retrieve a specific post by ID.

    This route allows users to retrieve a specific post from the database by providing its ID.

    Args:
        post_id (int): The unique identifier of the post to retrieve.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the specified post ID is not found in the database.

    Examples:
        A sample successful response:
        {
            'id': 1,
            'title': 'First Post',
            'content': 'This is the content of the first post.',
            'author': 'John Doe'
        }
    """
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
        return jsonify(post_data), HTTPStatus.OK
    else:
        return jsonify({'message': 'Post not found!'}), HTTPStatus.BAD_REQUEST


@app.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    """
    Update a post.

    This route allows authenticated users to update their own posts by providing a new title and content.

    Args:
        current_user (User): The currently authenticated user.
        post_id (int): The unique identifier of the post to update.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the specified post ID is not found in the database.
        BadRequest: If the current user is not the author of the post.

    Examples:
        A sample successful response:
        {
            'message': 'Post updated successfully!'
        }
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    # Query the post from the database
    post = model.Post.query.get(post_id)

    # Check if the post exists
    if not post:
        return jsonify({'message': 'Post not found!'}), HTTPStatus.BAD_REQUEST

    # Check if the current user is the author of the post
    if post.author != current_user:
        return jsonify({'message': 'You are not authorized to update this post!'}), HTTPStatus.BAD_REQUEST

    # Update the post attributes
    post.title = title
    post.content = content

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Post updated successfully!'}), HTTPStatus.OK


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """
    Delete a post.

    This route allows authenticated users to delete their own posts.

    Args:
        current_user (User): The currently authenticated user.
        post_id (int): The unique identifier of the post to delete.

    Returns:
        tuple: A tuple containing JSON response data and HTTP status code.

    Raises:
        BadRequest: If the specified post ID is not found in the database.
        BadRequest: If the current user is not the author of the post.

    Examples:
        A sample successful response:
        {
            'message': 'Post deleted successfully!'
        }
    """
    # Query the post from the database
    post = model.Post.query.get(post_id)

    # Check if the post exists
    if not post:
        return jsonify({'message': 'Post not found!'}), HTTPStatus.BAD_REQUEST

    # Check if the current user is the author of the post
    if post.author != current_user:
        return jsonify({'message': 'You are not authorized to delete this post!'}), HTTPStatus.BAD_REQUEST

    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted successfully!'}), HTTPStatus.OK


if __name__ == '__main__':
    app.run(debug=True)
