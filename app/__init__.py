from flask_mongoengine import MongoEngine
db = MongoEngine()


def create_app(config_key):

    # create instance
    from flask import Flask
    app = Flask(__name__)

    # load config
    from config import config_map
    app.config.from_object(config_map[config_key])
    config_map[config_key].init_app(app)

    # init extension
    db.init_app(app)

    # register blueprint
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
