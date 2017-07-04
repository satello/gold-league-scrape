from flask import request, jsonify
from flask.views import MethodView

from webapp.model import Owners, Players, db
from webapp.tasks.players import update_player_values, get_player_redraft_data
from webapp.tasks.google import get_team_information, get_player_information_for_team
from config import config

def register_task_routes(blueprint):
    view_func = PlayerValues.as_view('update_player_values')
    blueprint.add_url_rule('/update/values', strict_slashes=False, view_func=view_func, methods=['GET'])

    view_func = TeamInfo.as_view('team_info')
    blueprint.add_url_rule('/update/teams', strict_slashes=False, view_func=view_func, methods=['GET'])

    view_func = PlayerInfo.as_view('player_info')
    blueprint.add_url_rule('/update/players', strict_slashes=False, view_func=view_func, methods=['GET'])

    view_func = PlayerRedraft.as_view('player_redraft')
    blueprint.add_url_rule('/update/redraft', strict_slashes=False, view_func=view_func, methods=['GET'])

class PlayerValues(MethodView):

    def get(self):
        update_player_values()

        return jsonify("ok"), 200

class TeamInfo(MethodView):

    def get(self):
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

class PlayerInfo(MethodView):

    def get(self):
        owners = Owners.query.all()

        for owner in owners:
            # players from google sheet
            players = get_player_information_for_team(owner.name)
            # players in the db that are currently owned by team
            current_player_names = map(lambda x: x.name, Players.query.filter_by(owner_id=owner.id).all())

            # get the players that need to be removed
            players_diff = [x for x in current_player_names if x not in map(
                lambda x: config["name_differences"][x["player_name"]] if config["name_differences"].get(x["player_name"]) else x["player_name"], players)]

            # reset player info if no longer on team
            for player in players_diff:
                remove_player = Players.query.filter_by(name=player).first()
                remove_player.owner = None
                remove_player.cost = None
                remove_player.years = None
                db.session.add(remove_player)

            # add owner and contract data to player
            for player_info in players:
                name = config["name_differences"][player_info["player_name"]] if config["name_differences"].get(player_info["player_name"]) else player_info["player_name"]
                cur_player = Players.query.filter_by(name=name).first()

                if cur_player:
                    cur_player.owner = owner
                    cur_player.cost = player_info["price"]
                    cur_player.years = player_info["years_remaining"]
                    db.session.add(cur_player)

        db.session.commit()
        return jsonify('ok'), 201

class PlayerRedraft(MethodView):

    def get(self):
        get_player_redraft_data()
        return jsonify({}), 200
