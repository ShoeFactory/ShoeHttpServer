import requests
import pprint
import json

from threading import Thread


def send_async_qrcode(phone_number, validate_number):

    # url
    host_path = 'http://sms.market.alicloudapi.com/singleSendSms'

    # header
    app_code = 'b856ac7c95604275a313ef0f863cb913'
    headers = {'Authorization': 'APPCODE ' + app_code}

    # params
    param_dict = {'num': validate_number}
    param_string = json.dumps(param_dict)
    receive_num = phone_number
    sign_name = '闪客大'
    template_code = 'SMS_63025302'

    # request
    payload = {'ParamString': param_string,
               'RecNum': receive_num,
               'SignName': sign_name,
               'TemplateCode': template_code}

    r = requests.get(host_path, params=payload, headers=headers)

    if r.status_code == requests.codes.ok:
        if r.json()['success']:
            return True
    pprint.pprint(r.text)
    return False


def send_sms_qrcode(phone_number, validate_number):
    thr = Thread(target=send_async_qrcode, args=[phone_number, validate_number])
    thr.start()
    return thr
