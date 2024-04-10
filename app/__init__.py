from flask import Flask
from flask_sqlalchemy import SQLAlchemy

dia = 'mysql'
dri = 'pymysql'
username = 'root'
password = 'password'
host = 'localhost'
port = '3306'
database = 'blog_1'

# SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(dia, dri, username, password, host, port, database)
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(dia, dri, username, password, host, port, database)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
from . import blogApp