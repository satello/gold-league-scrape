from flask import Blueprint, jsonify

# routes
from webapp.api.tasks import register_task_routes

api = Blueprint('api', __name__)

register_task_routes(api)
