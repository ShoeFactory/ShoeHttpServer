from . import api
from ..model import User, LoggedUser, RegisterQrcode, PasswordQrcode, Device, UserDeviceBind
from ..sms import send_sms_qrcode
from flask import request
from flask import jsonify
from mongoengine.errors import NotUniqueError
from datetime import datetime
import random
from .authtoken import auth, get_user_by_token
import json

@api.route('/account/register/qrcode', methods=['POST', ])
def register_qrcode():
    # get telephone
    requestBody = json.loads(request.data)
    telephone = requestBody['telephone']

    # if already registered
    user = User.objects(telephone=telephone).first()

    if user is not None:
        return jsonify(code=1, message='telephone already registered')

    # generate qrcode
    qrcode = str(random.randint(100000, 1000000))

    # send qrcode to user by SMS
    send_sms_qrcode(telephone, qrcode)

    # record qrcode to database
    new_qrcode = RegisterQrcode(telephone=telephone,
                                qrcode=qrcode,
                                created=datetime.utcnow())
    new_qrcode.save()

    return jsonify(code=0, message='register_qrcode')


@api.route('/account/register', methods=['POST', ])
def register():
    # get form data
    requestBody = json.loads(request.data)
    telephone = requestBody['telephone']
    password = requestBody['password']
    qrcode = requestBody['qrcode']
    name = requestBody['name']

    # validate qrcode
    qrcodes = RegisterQrcode.objects(telephone=telephone)

    if qrcode not in [temp.qrcode for temp in qrcodes]:
        return jsonify(code=1, message='qrcode invalid')

    new_user = User(telephone=telephone, name=name)
    new_user.password = password

    try:
        new_user.save()
    except NotUniqueError:
        return jsonify(code=2, message='telephone already registered')

    return jsonify(code=0, message='add succeed')


@api.route('/account/login', methods=['POST'], )
def login():
    # get form data
    requestBody = json.loads(request.data)
    telephone = requestBody['telephone']
    password = requestBody['password']

    # find the user and validate the password md5
    user = User.objects(telephone=telephone).first()

    if not (user is not None and user.verify_password(password)):
        return jsonify(code=1, message='telephone or password wrong')

    # generate a token
    token = user.generate_token()

    # store token into db
    old_users = User.objects(telephone=telephone)
    old_logged_users = LoggedUser.objects(user__in=old_users)
    for logged_users in old_logged_users:
        logged_users.delete()

    logged_user = LoggedUser(user, token)
    logged_user.save()

    # return
    result = {
        "code": 0,
        "message": "login ok",
        "data": {
            "token": token,
        }
    }
    return jsonify(result)


@api.route('/account/password/qrcode', methods=['POST', ])
def password_qrcode():
    # get telephone
    requestBody = json.loads(request.data)
    telephone = requestBody['telephone']

    # generate qrcode
    qrcode = str(random.randint(100000, 1000000))

    # send qrcode to user by SMS
    send_sms_qrcode(telephone, qrcode)

    # record qrcode to database
    new_qrcode = PasswordQrcode(telephone=telephone,
                                qrcode=qrcode,
                                created=datetime.utcnow())
    new_qrcode.save()
    return jsonify(code=0, message='password_qrcode')


@api.route('/account/password/retrieve', methods=['POST', ])
def password_retrieve():
    # get form data
    requestBody = json.loads(request.data)
    telephone = requestBody['telephone']
    qrcode = requestBody['qrcode']
    newpassword = requestBody['newpassword']

    # validate the qrcode
    qrcodes = PasswordQrcode.objects(telephone=telephone)

    if qrcode not in [temp.qrcode for temp in qrcodes]:
        return jsonify(code=1, message='qrcode invalid')

    # reset the password
    user = User.objects(telephone=telephone).first()

    if user is None:
        return jsonify(code=2, message='telephone invalid')

    user.password = newpassword
    user.save()
    return jsonify(code=0, message='password reset success')


@api.route('/account/password/update', methods=['POST', ])
@auth.login_required
def password_update():
    # get form data
    requestBody = json.loads(request.data)
    new_password = requestBody['new_password']

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    user.password = new_password
    user.save()
    return jsonify(code=0, message='password update success')


@api.route('/account/profile', methods=['POST', ])
@auth.login_required
def get_user_profile():

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    print(user)

    result = {
        "code": 0,
        "data": {
            "name": user.name,
        }
    }
    return jsonify(result)


@api.route('/account/profile/update', methods=['POST', ])
@auth.login_required
def profile_update():
    # get form data
    requestBody = json.loads(request.data)
    new_name = requestBody['new_name']

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    user.name = new_name
    user.save()
    return jsonify(code=0, message='profile update success')


@api.route('/account/devices', methods=['POST', ])
@auth.login_required
def devices():
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    binds = UserDeviceBind.objects(user__in=[user])

    result = {
        "code": 0,
        "data": {
            "devices": [bind.to_json_dict() for bind in binds]
        }
    }

    return jsonify(result)


@api.route('/account/devices/add', methods=['POST', ])
@auth.login_required
def devices_add():
    # device
    requestBody = json.loads(request.data)
    sid = requestBody['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        device = Device(sid=sid)
        device.save()

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # bind
    name = requestBody['name']

    bind = UserDeviceBind.objects(user__in=[user], device__in=[device]).first()
    if bind is None:
        bind = UserDeviceBind(user=user, device=device, name=name)

    bind.name = name
    bind.save()
    return jsonify(code=0, message='add device success')


@api.route('/account/devices/remove', methods=['POST'], )
def devices_remove():
    # device
    requestBody = json.loads(request.data)
    sid = requestBody['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        return jsonify(code=1, message='wrong sid, no such device')

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # remove bind
    bind = UserDeviceBind.objects(device__in=[device], user__in=[user]).first()
    if bind is None:
        return jsonify(code=2, message='wrong sid, no such bind before')
    else:
        bind.delete()
        return jsonify(code=0, message='device removed')



