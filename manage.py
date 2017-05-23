from flask_script import Manager
from app import create_app

app_instance = create_app('development')
manager = Manager(app_instance)


if __name__ == '__main__':
    manager.run()
