from . import api
from flask import jsonify


@api.app_errorhandler(400)
def unauthorized(e):
    response = jsonify(success=False, msg='bad request')
    response.status_code = 400
    return response


@api.app_errorhandler(403)
def unauthorized(e):
    response = jsonify(success=False, msg='unauthorized')
    response.status_code = 403
    return response


@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify(success=False, msg='error_url')
    response.status_code = 404
    return response


@api.app_errorhandler(405)
def unauthorized(e):
    response = jsonify(success=False, msg='wrong method')
    response.status_code = 405
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify(success=False, msg='server_error')
    response.status_code = 500
    return response
