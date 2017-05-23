from . import api
from flask import jsonify


@api.route('/hello')
def say_hello():
    return jsonify(greet='hello',
                   to='world')
