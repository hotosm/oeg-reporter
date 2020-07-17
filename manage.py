
from server import create_app
from flask_script import Manager

application = create_app()
manager = Manager(application)

if __name__ == "__main__":
    manager.run()
