# http://blog.miguelgrinberg.com/post/flask-migrate-alembic-database-migration-wrapper-for-flask
import os

from flask_script import Manager
from flask_migrate import MigrateCommand

from webapp.app import create_app
from webapp import model

db = model.db

manager = Manager(create_app(os.environ.get('DB_URI')))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
