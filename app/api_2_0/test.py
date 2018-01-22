from . import api
from flask import jsonify


@api.route('/hellooo', methods=['GET', ])
def say_hello():
    return jsonify(greet='hello',
                   to='world')
