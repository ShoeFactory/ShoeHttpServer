from . import api
from ..model import User, LoggedUser, RegisterQrcode, PasswordQrcode, Device, LoggedDevice, UserDeviceBind
from flask import request
from flask import jsonify
from mongoengine.errors import NotUniqueError
from datetime import datetime
import random
from .authtoken import auth, get_user_by_token
import json


@api.route('/devicemanager/setpower', methods=['POST'], )
def setpower():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']
    power = requestBody["power"]

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    device.power = power
    device.save()

    return jsonify(code=0, message='set device power success')


@api.route('/devicemanager/setisonline', methods=['POST'], )
def setisonline():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']
    isOnline = requestBody["isOnline"]

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    device.is_online = isOnline
    device.save()

    return jsonify(code=0, message='set device isonline success')


@api.route('/devicemanager/setissubscribed', methods=['POST'], )
@auth.login_required
def setissubscribed():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']
    is_subscribed = requestBody["isSubscribed"]

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # 找到当前用户所有的设备
    binds = UserDeviceBind.objects(user__in=[user])
    for bind_device in binds:
        if bind_device.device.sid == imei:
            bind_device.is_subscribed = is_subscribed
            bind_device.save()

    return jsonify(code=0, message='set device issubscribed success')


@api.route('/devicemanager/getstatus', methods=['POST'], )
@auth.login_required
def devices_getstatus():
    # 找到当前用户
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    result = []

    # 找到当前用户所有的设备
    binds = UserDeviceBind.objects(user__in=[user])
    for bind_device in binds:
        device_status = {}

        device_status["imei"] = bind_device.device.sid
        device_status["power"] = bind_device.device.power
        device_status["isOnline"] = bind_device.device.is_online

        device_status["name"] = bind_device.name
        device_status["isSubscribed"] = bind_device.is_subscribed

        result.append(device_status)

    return jsonify(code=0, message='isonline require success', data=result)
