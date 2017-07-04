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


def register_player_routes(blueprint):
    players_view_func = PlayersRoutes.as_view('players')
    blueprint.add_url_rule('/players', strict_slashes=False, view_func=players_view_func, methods=['GET'])
    blueprint.add_url_rule('/players/<string:player_name>', strict_slashes=False, view_func=players_view_func, methods=['GET'])

    team_players_view_func = TeamPlayers.as_view('team_players')
    blueprint.add_url_rule('/teams/<string:owner_name>/players', strict_slashes=False, view_func=team_players_view_func, methods=['GET'])
    free_agent_view_func = FreeAgentPlayers.as_view('free_agents')
    blueprint.add_url_rule('/players/free-agents', strict_slashes=False, view_func=free_agent_view_func, methods=['GET'])

class PlayersRoutes(MethodView):

    def get(self, player_name=None):
        if player_name:
            # would be nice to DRY this shit out
            if USE_MEM_DB:
                player = mem_db.fetch_player_by_name(player_name=player_name)
            else:
                player = Players.query.filter_by(name=player_name).first()

            if not player:
                return jsonify(error="Unable to find player %s" % player_name), 400
            return jsonify(player.as_json()), 200

        position = request.args.get('position')

        if position:
            if USE_MEM_DB:
                all_players = mem_db.fetch_players_by_position(position=position)
            else:
                all_players = Players.query.filter_by(position=position).order_by(Players.value.desc()).all()
        else:
            if USE_MEM_DB:
                all_players = mem_db.fetch_all_players(no_picks=True)
            else:
                all_players = Players.query.filter(Players.position != "PICK").order_by(Players.value.desc()).all()

        return jsonify([p.as_json() for p in all_players]), 200

class TeamPlayers(MethodView):

    def get(self, owner_name):
        if USE_MEM_DB:
            team_players = mem_db.fetch_players_by_owner(owner_name=owner_name)
        else:
            owner = Owners.query.filter_by(name=owner_name).first()
            if not owner:
                return jsonify(error="Unable to find owner %s" % owner_name), 400

                team_players = Players.query.filter_by(owner=owner).order_by(Players.value.desc()).all()

        return jsonify(players=[p.as_json() for p in team_players]), 200


class FreeAgentPlayers(MethodView):

    def get(self):
        position = request.args.get('position')
        if position:
            if USE_MEM_DB:
                free_agents = mem_db.fetch_free_agents(no_picks=True)
                free_agents = [fa for fa in free_agents if fa.position == position]
            else:
                free_agents = Players.query.filter_by(position=position).filter_by(owner=None).order_by(Players.value.desc()).all()
        else:
            if USE_MEM_DB:
                free_agents = mem_db.fetch_free_agents(no_picks=True)
            else:
                free_agents = Players.query.filter(Players.position != "PICK").filter_by(owner=None).order_by(Players.value.desc()).all()

        return jsonify([p.as_json() for p in free_agents]), 200
