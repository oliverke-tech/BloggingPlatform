from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

api.add_resource(register_user, '/register')
api.add_resource(login_user, '/login')
api.add_resource(get_all_posts, '/posts')
api.add_resource(create_post, '/posts')

if __name__ == '__main__':
    app.run(debug=True)