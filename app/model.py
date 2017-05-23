# ORM: use classes to operate database

from flask import current_app
from . import db
from mongoengine import StringField, DateTimeField, PointField
from mongoengine import ListField, ReferenceField, EmbeddedDocumentField
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer
import random


class PositionRecord(db.EmbeddedDocument):
    datetime = DateTimeField()
    position = PointField()


class Device(db.Document):
    sid = StringField(required=True, unique=True)
    records = ListField(EmbeddedDocumentField(PositionRecord))


class User(db.Document):
    telephone = StringField(required=True, unique=True)
    password_hash = StringField()
    name = StringField()

    def get_password(self):
        raise AttributeError('password is not a readable attribute')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    password = property(get_password, set_password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        secret_key = current_app.config['SECRET_KEY']
        serializer = JSONWebSignatureSerializer(secret_key)
        bytes_token = serializer.dumps({'telephone': self.telephone,
                                        'random': random.random()})
        string_token = bytes_token.decode()
        return string_token


class LoggedUser(db.Document):
    user = ReferenceField(User)
    token = StringField()
    created = DateTimeField()
    meta = {
        'indexes': [
            {
                'fields': ['created'],
                'expireAfterSeconds': 60 * 60 * 24
            }
        ]
    }


class RegisterQrcode(db.Document):
    telephone = StringField()
    created = DateTimeField()
    qrcode = StringField()
    meta = {
        'indexes': [
            {
                'fields': ['created'],
                'expireAfterSeconds': 60 * 60 * 24
            }
        ]
    }


class PasswordQrcode(db.Document):
    telephone = StringField()
    created = DateTimeField()
    qrcode = StringField()
    meta = {
        'indexes': [
            {
                'fields': ['created'],
                'expireAfterSeconds': 60 * 60 * 24
            }
        ]
    }


class UserDeviceBind(db.Document):
    name = StringField()
    user = ReferenceField(User)
    device = ReferenceField(Device)

    def to_json_dict(self):
        return {'name': self.name, 'sid': self.device.sid}
