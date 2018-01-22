# ORM: use classes to operate database

from flask import current_app
from . import db
from mongoengine import StringField, DateTimeField, PointField, IntField, BooleanField
from mongoengine import ListField, ReferenceField, EmbeddedDocumentField
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer
import random


class Device(db.Document):
    sid = StringField(required=True, unique=True)
    last_online_time = StringField()
    power = IntField()

class LoggedDevice(db.Document):
    device = ReferenceField(Device)

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


class UserDeviceBind(db.Document):
    name = StringField()
    user = ReferenceField(User)
    device = ReferenceField(Device)

    def to_json_dict(self):
        return {'name': self.name, 'sid': self.device.sid}


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

class PositionRecord(db.Document):
    device = ReferenceField(Device)

    # 日期时间 yy-MM-dd hh:mm:ss C++
    # 日期时间 %Y-%m-%d %H:%M:%S Python
    datetime = DateTimeField()
    # 消息长度
    message_length = StringField()
    # 卫星个数
    satellite_count = StringField()
    # 经度
    longitude = StringField()
    # 维度
    latitude = StringField()
    # 速度
    speed = StringField()
    # 状态
    status = StringField()
    # 航向
    direction = StringField()

    def to_json_dict(self):
        return {'IMEI': self.device.sid,
                'datetime': self.datetime,
                'message_length': self.message_length,
                'satellite_count': self.satellite_count,
                'longitude': self.longitude,
                'latitude': self.latitude,
                'speed': self.speed,
                'status': self.status,
                'direction': self.direction}

    def from_json_dict(self, json):
        IMEI = json['IMEI']
        device = Device.objects(sid=IMEI).first()
        if device is None:
            return
        self.device = device
        self.datetime = json["datetime"]
        self.message_length = json["message_length"]
        self.satellite_count = json["satellite_count"]
        self.longitude = json["longitude"]
        self.latitude = json["latitude"]
        self.speed = json["speed"]
        self.status = json["status"]
        self.direction = json["direction"]
