import json

from config import config
from webapp.tasks.google import get_player_information_for_team, get_team_information, get_players_dynastyfftools_cloud_safe
from webapp.tasks.players import get_player_redraft_data

"""
Kind of confusing how this has to be done because of the crazy indexing thing I set up.
Essentially your app_data dict should look like:
{
    "players": [{
        "name": <str>,
        "position": <str>,
        "value": <int>
    }, ...],
    "team_players": [{
        "owner_name": <str>,
        "player": <name>,
        "cost": <int>,
        "years": <int>
    }, ...],
    "owners": [{
        "name": <str>,
        "cap_room": <int>,
        "spots_available": <int>,
        "years_remaining": <int>
    }, ...],
    "redraft": [{
        "player_name": <str>,
        "player_tier": <int>,
        "player_rank": <int>,
        "bye": <int>
    }, ...]
}
"""
if __name__ == "__main__":
    with open('app_data.json', 'w') as data_file:
        app_data = {
            "players": [],
            "owners": [],
            "redraft": [],
            "team_players": []
        }

        # load teams
        teams = get_team_information()
        # in correct format from tasks
        # NOTE could cause a bug if dict name changes in task
        app_data["owners"] = teams

        # load players
        players = get_players_dynastyfftools_cloud_safe()
        player_data = []
        player_lookup = {}
        for player_attributes in players:
            player_data.append({
                "name": player_attributes[0],
                "position": player_attributes[1],
                "value": int(player_attributes[5])
            })
            player_lookup[player_attributes[0]] = True

        app_data["players"] = player_data

        # load redraft data
        redraft = get_player_redraft_data(raw=True)
        redraft_data = []
        for data in redraft:
            safe_name = config["name_differences"].get(data["name"], data["name"])
            if not player_lookup.get(safe_name):
                print("skipping player %s" % safe_name)
                continue
            redraft_data.append({
                "player_name": safe_name,
                "tier": data["redraft_tier"],
                "player_rank": data["redraft_rank"],
                "player_bye": data["bye"]
            })

        app_data["redraft"] = redraft_data

        team_players_data = []
        for owner in app_data["owners"]:
            team_players = get_player_information_for_team(owner["name"])

            for player in team_players:
                safe_name = config["name_differences"].get(player["player_name"], player["player_name"])
                if not player_lookup.get(safe_name):
                    raise RuntimeError("Cannot find name %s" % safe_name)
                    continue
                team_players_data.append({
                    "owner_name": owner["name"],
                    "player": safe_name,
                    "cost": player["price"],
                    "years": player["years_remaining"]
                })

        app_data["team_players"] = team_players_data

        json.dump(app_data, data_file)
