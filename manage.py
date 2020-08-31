
from flask_script import Manager

from server import create_app

application = create_app()
manager = Manager(application)

if __name__ == "__main__":
    manager.run()
