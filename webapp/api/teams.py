import os
import random

from flask import request, jsonify
from flask.views import MethodView

from webapp.model import Owners, Players, db
from webapp.db import mem_db
from config import config

# can use either postgres or in memory storage
USE_MEM_DB = os.environ.get('USE_MEM_DB', True)

#
def register_teams_routes(blueprint):
    players_view_func = TeamRoutes.as_view('teams')
    blueprint.add_url_rule('/teams', strict_slashes=False, view_func=players_view_func, methods=['GET'])
    blueprint.add_url_rule('/teams/<string:owner_name>', strict_slashes=False, view_func=players_view_func, methods=['GET'])

#     team_players_view_func = TeamValues.as_view('team_values')
#     blueprint.add_url_rule('/teams/values/<string:owner_name>', strict_slashes=False, view_func=team_players_view_func, methods=['GET'])
#     blueprint.add_url_rule('/teams/values', strict_slashes=False, view_func=team_players_view_func, methods=['GET'])
#
class TeamRoutes(MethodView):

    def get(self, owner_name=None):
        shuffle = request.args.get('shuffle', False)
        print(request.query_string)
        print(shuffle)

        if owner_name:
            if USE_MEM_DB:
                team = mem_db.fetch_owner_by_name(owner_name)
            else:
                team = Owners.query.filter_by(name=owner_name).first()
            if not team:
                return jsonify(error="Unable to find team %s" % owner_name), 400
            return jsonify(team.as_json()), 200

        if USE_MEM_DB:
            teams = mem_db.fetch_all_owners()
        else:
            teams = Owners.query.all()

        teams = [team.as_json() for team in teams]
        # Randomize teams
        if shuffle:
            random.shuffle(teams)

        return jsonify(teams), 200
#
#
# class TeamValues(MethodView):
#
#     def get(self, owner_name=None):
#         position = request.args.get('position')
#
#         if owner_name:
#             team = Owners.query.filter_by(name=owner_name).first()
#             if not team:
#                 return jsonify(error="Unable to find team %s" % owner_name), 400
#
#             if position:
#                 all_players = Players.query.join(Owners).filter(Players.position == position).filter(Owners.name == owner.name).order_by(Players.value.desc()).all()
#             else:
#                 all_players = Players.query.join(Owners).filter(Owners.name == owner.name).order_by(Players.value.desc()).all()
#
#             value = 0
#             for p in all_players:
#                 value += p.value
#
#             return jsonify({owner_name: value}), 200
#         else:
#             owners = Owners.query.all()
#
#             owner_values = {}
#             for owner in owners:
#                 if position:
#                     all_players = Players.query.join(Owners).filter(Players.position == position).filter(Owners.name == owner.name).order_by(Players.value.desc()).all()
#                 else:
#                     all_players = Players.query.join(Owners).filter(Owners.name == owner.name).order_by(Players.value.desc()).all()
#
#                 value = 0
#                 for p in all_players:
#                     value += p.value
#
#                 owner_values[owner.name] = value
#
#             return jsonify(owner_values), 200
