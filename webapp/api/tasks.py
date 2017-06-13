from flask import request, jsonify
from flask.views import MethodView

from webapp.model import Owners, db
from webapp.tasks.update_player_values import update_player_values
from webapp.tasks.google import get_team_information

def register_task_routes(blueprint):
    view_func = PlayerValues.as_view('update_player_values')
    blueprint.add_url_rule('/update/values', strict_slashes=False, view_func=view_func, methods=['GET'])

    view_func = TeamInfo.as_view('team_info')
    blueprint.add_url_rule('/update/teams', strict_slashes=False, view_func=view_func, methods=['PUT'])

class PlayerValues(MethodView):

    def get(self):
        update_player_values()

        return jsonify("ok"), 200

class TeamInfo(MethodView):

    def put(self):
        teams = get_team_information()

        for team in teams:
            owner = Owners.query.filter_by(name=team["team_name"]).first()

            if not owner:
                new_owner = Owners(name=team['team_name'],
                                   cap_room=team['cap_room'],
                                   years_remaining=team['years_remaining'],
                                   spots_available=team['spots_available'])

                db.session.add(new_owner)
                continue
            else:
                for key, value in team.items():
                    if hasattr(owner, key):
                        setattr(owner, key, value)
                db.session.add(owner)
                continue

        db.session.commit()
        return jsonify('ok'), 201
