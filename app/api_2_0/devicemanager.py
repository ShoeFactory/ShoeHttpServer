from . import api
from ..model import User, LoggedUser, RegisterQrcode, PasswordQrcode, Device, LoggedDevice, UserDeviceBind
from flask import request
from flask import jsonify
from mongoengine.errors import NotUniqueError
from datetime import datetime
import random
from .authtoken import auth, get_user_by_token
import json

@api.route('/devicemanager/setonline', methods=['POST'], )
def device_online():
   
    requestBody = json.loads(request.data)
    imei = requestBody['sid']

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')
    
    # 更新device的最后登陆时间
    dt = datetime.now() 
    device.last_online_time = dt.strftime('%Y%m%d%H%M%S')
    device.save()

    # 判断是否已登陆
    old_logged = LoggedDevice.objects(device__in=[device]).first()
    if old_logged is None:
        loggedDevice = LoggedDevice(device=device)
        loggedDevice.save()
    return jsonify(code=0, message='set device online success')
   

@api.route('/devicemanager/setoffline', methods=['POST'], )
def device_offline():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']

    # 判断device有效性
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    # 移除
    loggedDevice = LoggedDevice.objects(device__in=[device]).first()
    if loggedDevice is not None:
        loggedDevice.delete()
    return jsonify(code=0, message='set device offline success')


@api.route('/devicemanager/isonline', methods=['POST'], )
@auth.login_required
def device_isonline():
    # 找到当前用户
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)
    print(user)

    # 找到当前用户所有的设备
    binds = UserDeviceBind.objects(user__in=[user])
    devices = [x.device for x in binds]
    
    # 查询设备是否登陆
    result = []
    for device in devices:
        logged = LoggedDevice.objects(device__in=[device]).first()
        if logged is not None:
            result.append(device.sid)
    return jsonify(code=0, message='isonline require success', data=result)   

@api.route('/devicemanager/setstatus', methods=['POST'], )
def device_setstatus():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']
    status = requestBody['status']
    power = status['power']

    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')
    device.power = power
    device.save()
    return jsonify(code=1, message='set status success')

@api.route('/devicemanager/getstatus', methods=['POST'], )
@auth.login_required
def devices_getstatus():
    # 找到当前用户
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # 找到当前用户所有的设备
    binds = UserDeviceBind.objects(user__in=[user])
    devices = [x.device for x in binds]

    # 查询设备的电量
    result = {}
    for device in devices:
        result[device.sid] = device.power
    return jsonify(code=0, message='isonline require success', data=result)
