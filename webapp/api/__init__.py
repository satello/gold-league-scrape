from flask import Blueprint, jsonify

# routes
from webapp.api.tasks import register_task_routes
from webapp.api.players import register_player_routes
from webapp.api.teams import register_teams_routes
from webapp.api.debug import register_debug_routes

api = Blueprint('api', __name__)

register_task_routes(api)
register_player_routes(api)
register_teams_routes(api)
register_debug_routes(api)
