from flask import jsonify
from . import api
from .authtoken import auth


@api.route('/position', methods=['GET', ])
@auth.login_required
def record():
    return jsonify(success=True, msg='get')


@api.route('/position/add', methods=['POST', ])
def record_add():
    return jsonify(success=True, msg='add')


@api.route('/position/remove', methods=['POST', ])
@auth.login_required
def record_remove():
    return jsonify(success=True, msg='remove')
