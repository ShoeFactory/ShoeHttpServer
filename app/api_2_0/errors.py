from . import api
from flask import jsonify


@api.app_errorhandler(400)
def bad_request(e):
    response = jsonify(success=False, msg='bad request')
    response.status_code = 400
    return response


@api.app_errorhandler(403)
def unauthorized(e):
    response = jsonify(code=403, msg='unauthorized')
    response.status_code = 403
    return response


@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify(code=404, message='error_url')
    response.status_code = 404
    return response


@api.app_errorhandler(405)
def wrong_request_method(e):
    response = jsonify(code=405, msg='wrong request method')
    response.status_code = 405
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify(code=500, msg='server_error')
    response.status_code = 500
    return response
