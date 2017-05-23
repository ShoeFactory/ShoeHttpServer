class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_DB = 'ShoePositionDev'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27072
    SECRET_KEY = 'wangxk'


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
