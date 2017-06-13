from flask import Blueprint, jsonify

# routes
from webapp.api.tasks import register_task_routes
from webapp.api.players import register_player_routes

api = Blueprint('api', __name__)

register_task_routes(api)
register_player_routes(api)
