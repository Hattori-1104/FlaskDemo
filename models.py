from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo")))


class User(UserMixin, db.Model):
    email = db.Column(db.String(160), primary_key=True, nullable=False)
    username = db.Column(db.String(40), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    auth_username = db.Column(db.String(40), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.email

"""
class Buy(db.Model):
    id = db.Column(db.String(16), nullable=False, primary_key=True)
    
"""