# http authentication in restful api

from flask_httpauth import HTTPTokenAuth
from flask import abort
from ..model import LoggedUser

auth = HTTPTokenAuth(scheme='Token', realm='Need a token')


@auth.verify_token
def verify_token(token):
    logged_user = LoggedUser.objects(token=token).first()
    if logged_user is None:
        return False
    return True


@auth.error_handler
def auth_error():
    abort(403)


def get_user_by_token(token):
    user = LoggedUser.objects(token=token).first()
    return user.user
