# Blogging Platform
This Flask application provides an API for managing user authentication and creating, retrieving, updating, and deleting blog posts.

## Installation

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. Set up the database:
    Ensure you have MySQL installed and running. Update the database configuration in `app/__init__.py` with your MySQL credentials:

    ```python
    dia = 'mysql'
    dri = 'pymysql'
    username = 'your_username'
    password = 'your_password'
    host = 'localhost'
    port = '3306'
    database = 'blog_1'
    ```

    Then, create a database by running the following command (update root with your username):
    ```
    mysql -h localhost -u root -p
    (input password)
    CREATE DATABASE blog_1;
    ```

## Usage

1. Run the Flask application:
    ```
    python3 run.py runserver
    ```

2. Once the server is running, you can interact with the API using HTTP requests. Below are the available routes:

    - `/signup` (POST): Register a new user by providing a username and password in the request body.
        ```
        curl localhost:5050/signup -X POST -d '{"username":"your_username", "password":"your_password"}' -H 'Content-Type: application/json'
        ```

    - `/signin` (POST): Sign in with a registered username and password to receive a JWT token for authentication.
        ```
        curl localhost:5050/signin -X POST -d '{"username":"your_username", "password":"your_password"}' -H 'Content-Type: application/json'
        ```

    - `/posts` (POST): Create a new blog post. Authentication required. Provide title and content in the request body.
        ```
        curl localhost:5050/posts -X POST -H 'Authorization: Bearer <your_token>' -d '{"title":"your_title", "content":"your_content"}' -H 'Content-Type: application/json'
        ```

    - `/posts` (GET): Retrieve all blog posts.
        ```
        curl localhost:5050/posts
        ```

    - `/posts/<post_id>` (GET): Retrieve a specific blog post by its ID.
        ```
        curl localhost:5050/posts/<post_id>
        ```

    - `/posts/<post_id>` (PUT): Update a blog post by its ID. Authentication required. Provide title and content in the request body.
        ```
        curl localhost:5050/posts/<post_id> -X PUT -H 'Authorization: Bearer <your_token>' -d '{"title":"updated_title", "content":"updated_content"}' -H 'Content-Type: application/json'
        ```

    - `/posts/<post_id>` (DELETE): Delete a blog post by its ID. Authentication required.
        ```
        curl -X DELETE localhost:5050/posts/<post_id> -H 'Authorization: Bearer <your_token>'
        ```

## Authentication

Authentication is handled using JSON Web Tokens (JWT). Upon signing in, a JWT token is generated and provided in the response. This token must be included in the `Authorization` header of subsequent requests to authenticate the user.

## Unit Testing

Unit tests are implemented to ensure the functionality of the application. To run the unit tests, execute the following command:

```
python3 -m test.py
```

## Contributor

- Zhengyu(Oliver) Ke