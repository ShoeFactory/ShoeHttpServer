from flask import jsonify, request
from . import api
from .authtoken import auth, get_user_by_token
from ..model import PositionRecord, Device, UserDeviceBind
from datetime import datetime


@api.route('/position/add', methods=['POST', ])
def record_add():
    position_record = PositionRecord()
    position_record.from_json_dict(request.form)

    if position_record.device is None:
        return jsonify(success=False, msg='imei not bind yet')
    else:
        position_record.save()
        return jsonify(success=True, msg='position added')


@api.route('/position/remove', methods=['POST', ])
@auth.login_required
def record_remove():
    return jsonify(success=True, msg='position removed')


# 最新的位置信息
@api.route('/position/latest', methods=['POST', ])
@auth.login_required
def record_latest():
    # device
    sid = request.form['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        return jsonify(success=False, msg='no device has such sid')

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # bind
    bind = UserDeviceBind.objects(user__in=[user], device__in=[device]).first()
    if bind is None:
        return jsonify(success=False, msg='no device has bind')

    # latest_record
    record = PositionRecord.objects(device__in=[device]).order_by('-datetime').first()

    if record is None:
        return jsonify(success=False, msg='no record yet')
    else:
        return jsonify(success=True, record=record.to_json_dict())


# 时间段的位置信息
@api.route('/position/latest', methods=['POST', ])
@auth.login_required
def record_periods():
    # device
    sid = request.form['sid']
    device = Device.objects(sid=sid).first()
    if device is None:
        return jsonify(success=False, msg='no device has such sid')

    # user
    auth_type, token = request.headers['Authorization'].split(None, 1)
    user = get_user_by_token(token)

    # bind
    bind = UserDeviceBind.objects(user__in=[user], device__in=[device]).first()
    if bind is None:
        return jsonify(success=False, msg='no device has bind')

    # records
    start_string = request.form['start']
    start = datetime.strftime(start_string, '%Y-%m-%d %H:%M:%S')
    stop_string = request.form['stop']
    stop = datetime.strftime(stop_string, '%Y-%m-%d %H:%M:%S')

    records = PositionRecord.objects(datetime__gte=start, datetime__lt=stop, device__in=[device]).order_by('-datetime')

    return jsonify(success=True, records=[record.to_json_dict() for record in records])




