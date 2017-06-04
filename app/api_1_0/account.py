from . import api
from ..model import User, LoggedUser, RegisterQrcode, PasswordQrcode, Device, UserDeviceBind
from ..sms import send_sms_qrcode
from flask import request
from flask import jsonify
from mongoengine.errors import NotUniqueError
from datetime import datetime
import random
from .authtoken import auth, get_user_by_token


@api.route('/account/register/qrcode', methods=['POST', ])
def register_qrcode():
    # get telephone
    telephone = request.form['telephone']

    # generate qrcode
    qrcode = str(random.randint(100000, 1000000))

    # send qrcode to user by SMS
    send_sms_qrcode(telephone, qrcode)

    # record qrcode to database
    new_qrcode = RegisterQrcode(telephone=telephone,
                                qrcode=qrcode,
                                created=datetime.utcnow())
    new_qrcode.save()

    return jsonify(success=True, to='5', msg='register_qrcode')


@api.route('/account/register', methods=['POST', ])
def register():
    # get form data
    telephone = request.form['telephone']
    password = request.form['password']
    qrcode = request.form['qrcode']
    name = request.form['name']

    # validate qrcode
    qrcodes = RegisterQrcode.objects(telephone=telephone)

    if qrcode not in [temp.qrcode for temp in qrcodes]:
        return jsonify(success=False, msg='qrcode invalid')

    new_user = User(telephone=telephone, name=name)
    new_user.password = password

    try:
        new_user.save()
    except NotUniqueError:
        return jsonify(success=False, msg='telephone already registered')

    return jsonify(success=True, msg='add')


@api.route('/account/login', methods=['POST'], )
def login():
    # get form data
    telephone = request.form['telephone']
    password = request.form['password']

    # find the user and validate the password md5
    user = User.objects(telephone=telephone).first()

    if not (user is not None and user.verify_password(password)):
        return jsonify(success=False, msg='telephone or password wrong')

    # generate a token
    token = user.generate_token()
    print(type(token))

    # store token into db
    old_users = User.objects(telephone=telephone)
    old_logged_users = LoggedUser.objects(user__in=old_users)
    for logged_users in old_logged_users:
        logged_users.delete()

    logged_user = LoggedUser(user, token)
    logged_user.save()

    # return
    return jsonify(success=True, token=token)


@api.route('/account/password/qrcode', methods=['POST', ])
def password_qrcode():
    # get telephone
    telephone = request.form['telephone']

    # generate qrcode
    qrcode = str(random.randint(100000, 1000000))

    # send qrcode to user by SMS
    send_sms_qrcode(telephone, qrcode)

    # record qrcode to database
    new_qrcode = PasswordQrcode(telephone=telephone,
                                qrcode=qrcode,
                                created=datetime.utcnow())
    new_qrcode.save()
    return jsonify(success=True, msg='password_qrcode')


@api.route('/account/password/retrieve', methods=['POST', ])
def password_retrieve():
    # get form data
    telephone = request.form['telephone']
    qrcode = request.form['qrcode']
    newpassword = request.form['newpassword']

    # validate the qrcode
    qrcodes = PasswordQrcode.objects(telephone=telephone)

    if qrcode not in [temp.qrcode for temp in qrcodes]:
        return jsonify(success=False, msg='qrcode invalid')

    # reset the password
    user = User.objects(telephone=telephone).first()

    if user is None:
        return jsonify(success=False, msg='telephone invalid')

    user.password = newpassword
    user.save()
    return jsonify(success=True, msg='password reset success')


@api.route('/account/devices')
@auth.login_required
def devices():
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    binds = UserDeviceBind.objects(user__in=[user])

    # bind = binds.first()
    # aaa = bind.to_json_dict()
    # return jsonify(success=True, devices=aaa)

    return jsonify(success=True, devices=[bind.to_json_dict() for bind in binds])


@api.route('/account/devices/add', methods=['POST', ])
@auth.login_required
def devices_add():
    # device
    sid = request.form['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        device = Device(sid=sid)
        device.save()

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # bind
    name = request.form['name']

    bind = UserDeviceBind.objects(user__in=[user], device__in=[device]).first()
    if bind is None:
        bind = UserDeviceBind(user=user, device=device, name=name)

    bind.name = name
    bind.save()
    return jsonify(success=True, msg='add device success')


@api.route('/account/devices/remove', methods=['POST'], )
def devices_remove():
    # device
    sid = request.form['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        return jsonify(success=False, msg='wrong sid, no such device')

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # remove bind
    bind = UserDeviceBind.objects(device__in=[device], user__in=[user]).first()
    if bind is None:
        return jsonify(success=False, msg='wrong sid, no such bind before')
    else:
        bind.delete()
        return jsonify(success=True, msg='device removed')



