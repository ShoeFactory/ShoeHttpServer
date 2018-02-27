from flask import jsonify, request
from . import api
from .authtoken import auth, get_user_by_token
from ..model import PositionRecord, Device, UserDeviceBind, PositionGPS, PositionWifiLBS
from datetime import datetime
import json
from threading import Thread
import requests
import pprint


@api.route('/position/addgps', methods=['POST', ])
def position_addgps():
    requestBody = json.loads(request.data)
    imei = requestBody['sid']

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    # 添加记录
    gps = requestBody['gps']
    new_gps = PositionGPS(datetime=gps['datetime'],
                          latitude=gps['latitude'],
                          longitude=gps['longitude'])
    device.gps_list.append(new_gps)
    device.save()
    return jsonify(code=0, message='add gps succeed')


def cellocation_api(mcc, mnc, lac, cellid):
    host_path = "http://api.cellocation.com:81/cell/"

    #  转换进制 lac cellid 是16进制的
    ten_lac = int(lac, 16)
    ten_cellid = int(cellid, 16)
    payload = {'mcc': mcc, 'mnc': mnc, 'lac': ten_lac, 'ci': ten_cellid, 'output': "json"}
    r = requests.get(host_path, params=payload)
    if r.status_code == requests.codes.ok:
        if r.json()['errcode'] == 0:
            return {"code": 0, "latitude": r.json()['lat'], "longitude": r.json()['lon']}
        else:
            return {"code": 2, "message": "api_response_content_error"}
    return {"code": 3, "messaage": "api_error"}


# 传入wifilbs结构体
def caculate_wifilbs_to_gps(position_wifiLBS):
    if len(position_wifiLBS.lbs_list) < 1:
        return
    else:
        first_lbs = position_wifiLBS.lbs_list.first()
        gps_revert_result = cellocation_api(first_lbs.mcc, first_lbs.mnc, first_lbs.lac, first_lbs.cellid)

        if gps_revert_result["code"] == 0:
            caculated_gps = PositionGPS(datetime=position_wifiLBS.dateTime)
            caculated_gps.longitude = float(gps_revert_result["longitude"])
            caculated_gps.latitude = float(gps_revert_result["latitude"])
            position_wifiLBS.caculated_gps = caculated_gps
            position_wifiLBS.save()
        else:
            pprint.pprint(gps_revert_result)


@api.route('/position/addwifilbs', methods=['POST', ])
def position_addwifilbs():

    requestBody = json.loads(request.data)
    imei = requestBody['sid']

    # 判断设置是否存在 否则是野设备
    device = Device.objects(sid=imei).first()
    if device is None:
        return jsonify(code=1, message='device not binded yet')

    # 添加记录
    position_wifilbs = PositionWifiLBS()
    position_wifilbs.from_json_dict(requestBody['wifilbs'])
    device.wifilbs_list.append(position_wifilbs)
    device.save()

    caculate_wifilbs_to_gps(position_wifilbs)
    return jsonify(code=0, message='add wifilbs succeed')


# 暂时不做记录删除功能
@api.route('/position/remove', methods=['POST', ])
@auth.login_required
def record_remove():
    return jsonify(success=True, msg='position removed')


# 最新的位置信息 接收一个device列表 按照字典返回
@api.route('/position/latest', methods=['POST', ])
@auth.login_required
def record_latest():
    requestBody = json.loads(request.data)

    type = requestBody['type']
    imeis = requestBody['sids']

    result = []
    # 遍历device列表
    for imei in imeis:

        device_gps = {}
        device_gps["imei"] = imei
        device_gps["lan"] = 116.380122
        device_gps["lon"] = 39.932863
        device_gps["name"] = "test"
        result.append(device_gps)

        device = Device.objects(sid=imei).first()

        if device is None:
            continue
        else:
            # 全部的
            if type == 0:
                pass
            # 只取gps
            elif type == 1:
                gps_list = device.gps_list

            # 只取lbs计算的gps
            elif type == 2:
                lbs_list = device.wifilbs_list

    return jsonify(code=0, data=result)


# 时间段的位置信息
@api.route('/position/period', methods=['POST', ])
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




