from flask import Flask
from flask_sqlalchemy import SQLAlchemy

dia = 'mysql'
dri = 'pymysql'
username = 'admin'
password = 'password'
host = 'localhost'
port = '3306'
database = 'ece1779_a2'

# SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(dia, dri, username, password, host, port, database)
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(dia, dri, username, password, host, port, database)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
from app import app