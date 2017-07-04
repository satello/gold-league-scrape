import os

from flask import request, jsonify
from flask.views import MethodView

from webapp.model import Owners, Players, db
from webapp.db import mem_db
from webapp.tasks.players import update_player_values
from webapp.tasks.google import get_team_information, get_player_information_for_team
from config import config

# can use either postgres or in memory storage
USE_MEM_DB = os.environ.get('USE_MEM_DB', True)


def register_debug_routes(blueprint):
    mem_db_player_view_func = MemDbPlayers.as_view('mem_db_players_debug')
    blueprint.add_url_rule('/debug/mem_db/players', strict_slashes=False, view_func=mem_db_player_view_func, methods=['GET'])
    blueprint.add_url_rule('/debug/mem_db/players/<string:index_name>', strict_slashes=False, view_func=mem_db_player_view_func, methods=['GET'])
    mem_db_owner_view_func = MemDbOwners.as_view('mem_db_owners_debug')
    blueprint.add_url_rule('/debug/mem_db/owners', strict_slashes=False, view_func=mem_db_owner_view_func, methods=['GET'])
    blueprint.add_url_rule('/debug/mem_db/owners/<string:index_name>', strict_slashes=False, view_func=mem_db_owner_view_func, methods=['GET'])

class MemDbPlayers(MethodView):

    def get(self, index_name=None):
        if not index_name:
            return mem_db.Players.__str__()

        return jsonify(mem_db.Players._indexes[index_name].keys()), 200

class MemDbOwners(MethodView):

    def get(self, index_name=None):
        if not index_name:
            return mem_db.Owners.__str__()

        return jsonify(mem_db.Owners._indexes[index_name].keys()), 200
