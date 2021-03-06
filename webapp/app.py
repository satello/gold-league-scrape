import os
import logging
import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .api import api
from webapp.db import db, mem_db
# from webapp.middleware import init_middleware

# can use either postgres or in memory storage
USE_MEM_DB = os.environ.get('USE_MEM_DB', True)

def create_app(DB_URI=None):
    application = Flask(__name__)

    @application.before_request
    def enable_local_error_handling():
        application.logger.addHandler(logging.StreamHandler())
        application.logger.setLevel(logging.INFO)

    # DB Connection Information
    if not DB_URI and not USE_MEM_DB:
        DB_URI = os.environ.get('DB_URI', 'postgresql://localhost/goldleagueapp')

    if not USE_MEM_DB:
        application.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
        application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # initialize db. any external calls to db must use application context
        db.init_app(application)
        # set up migration support for alembic
        migrate = Migrate()
        migrate.init_app(application, db)

    # send CORS headers for frontend
    @application.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    # middleware
    # init_middleware(application)

    # application.url_map.default_subdomain = 'api'
    # Register route blueprints
    application.register_blueprint(api)

    # bootstrap from file
    if USE_MEM_DB:
        with open('app_data.json', 'r') as app_data:
            initial_values = json.load(app_data)
            mem_db.load_cache_from_dict(initial_values)

    return application
