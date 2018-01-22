from flask import Blueprint

api = Blueprint('api.2.0', __name__)

from . import errors, position, account, devicemanager, authtoken, test
