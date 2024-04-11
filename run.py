from app import app

app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = 'my_secret_key'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050', debug=True)