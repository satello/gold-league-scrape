import os

from flask import request, jsonify
from flask.views import MethodView

from webapp.model import Owners, Players, db
from webapp.db import mem_db
from webapp.memory_model import Player
from webapp.tasks.players import update_player_values, get_player_redraft_data
from webapp.tasks.google import get_team_information, get_player_information_for_team, get_players_dynastyfftools_cloud_safe
from config import config

# can use either postgres or in memory storage
USE_MEM_DB = os.environ.get('USE_MEM_DB', True)


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
        selenium_enabled = os.environ.get('SELENIUM_ENABLED', False)
        # enable selenium to get directly from source
        if (selenium_enabled):
            update_player_values()
        else:
            # use calebs spreadsheet for dyntastyff values
            players = get_players_dynastyfftools_cloud_safe()

            for player_attributes in players:
                name = player_attributes[0]
                position = player_attributes[1]
                value = int(player_attributes[5])

                if USE_MEM_DB:
                    mem_db.new_player_value(name, position, value)
                else:
                    Players.new_player_value(name, position, value)

        return jsonify("ok"), 200

class TeamInfo(MethodView):

    def get(self):
        teams = get_team_information()

        for team in teams:
            if USE_MEM_DB:
                owner = mem_db.fetch_owner_by_name(team["team_name"])
            else:
                owner = Owners.query.filter_by(name=team["team_name"]).first()

            if not owner:
                if USE_MEM_DB:
                    mem_db.new_owner(name=team['team_name'],
                                     cap_room=team['cap_room'],
                                     years_remaining=team['years_remaining'],
                                     spots_available=team['spots_available'])
                else:
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
                if not USE_MEM_DB:
                    db.session.add(owner)
                    continue

        if not USE_MEM_DB:
            db.session.commit()
        return jsonify('ok'), 201

class PlayerInfo(MethodView):

    def get(self):
        if USE_MEM_DB:
            owners = mem_db.fetch_all_owners()
        else:
            owners = Owners.query.all()

        for owner in owners:
            # players from google sheet
            players = get_player_information_for_team(owner.name)
            # players in the db that are currently owned by team
            if USE_MEM_DB:
                owner_players = mem_db.fetch_players_by_owner(owner_name=owner.name)
            else:
                owner_players = Players.query.filter_by(owner_id=owner.id).all()

            current_player_names = map(lambda x: x.name, owner_players)

            # get the players that need to be removed
            players_diff = [x for x in current_player_names if x not in map(
                lambda x: config["name_differences"][x["player_name"]] if config["name_differences"].get(x["player_name"]) else x["player_name"], players)]

            # reset player info if no longer on team
            for player in players_diff:
                if USE_MEM_DB:
                    remove_player = mem_db.fetch_player_by_name(player)
                    mem_db.remove_player_from_team(remove_player, owner.name)
                else:
                    remove_player = Players.query.filter_by(name=player).first()
                    remove_player.owner = None
                    remove_player.cost = None
                    remove_player.years = None
                    db.session.add(remove_player)

            # add owner and contract data to player
            for player_info in players:
                name = config["name_differences"][player_info["player_name"]] if config["name_differences"].get(player_info["player_name"]) else player_info["player_name"]

                if USE_MEM_DB:
                    cur_player = mem_db.fetch_player_by_name(name)
                else:
                    cur_player = Players.query.filter_by(name=name).first()

                if cur_player:
                    if USE_MEM_DB:
                        mem_db.add_player_to_team(cur_player, owner.name, player_info["price"], player_info["years_remaining"])
                    else:
                        cur_player.owner = owner
                        cur_player.cost = player_info["price"]
                        cur_player.years = player_info["years_remaining"]
                        db.session.add(cur_player)

        if not USE_MEM_DB:
            db.session.commit()
        return jsonify('ok'), 201

class PlayerRedraft(MethodView):

    def get(self):
        get_player_redraft_data()
        return jsonify({}), 200
