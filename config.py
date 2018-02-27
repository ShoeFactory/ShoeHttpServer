class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'wangxk'

    # mongoengine use pymongo internal
    # add connect:False make things all right
    MONGODB_SETTINGS = {
        'db': 'ShoePositionDev',
        'host': '127.0.0.1',
        'port': 27072,
        'connect': False
    }


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
