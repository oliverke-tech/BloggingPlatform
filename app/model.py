from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    # user_id = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return u"user('{self.username}')"


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    # body = db.Column(db.Text, nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # uploader = db.relationship('User', backref=db.backref('posts'))

    def to_json(self):
        json_post = {
            'title': self.title,
            'content': self.content,
        }
        return json_post