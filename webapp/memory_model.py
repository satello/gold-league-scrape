from bisect import insort_right

class MemoryModel:
    """
    Essentially a giant cache with helpers methods to mimic sqlalchemy model
    """

    def __init__(self, app_data=None):
        self.Players = Players()
        self.Owners = Owners()

        if app_data:
            self.load_cache_from_dict(app_data)

    # INSERTIONS AND UPDATES
    def new_player_value(self, name, position, value):
        existing_player = self.Players._indexes["name"].get(name)
        if existing_player:
            if existing_player.value != value:
                existing_player.value = value
                # need to remove and reinsert for sorting purposes
                self.Players.reindex_player(existing_player)
        else:
            self.Players._add(Player(name=name, position=position, value=value))

    def new_owner(self, name, cap_room, years_remaining, spots_available):
        self.Owners._add(Owner(name=name, cap_room=cap_room, years_remaining=years_remaining, spots_available=spots_available))

    def add_player_to_team(self, player, owner_name, cost=None, years=None):
        player.owner = owner_name
        player.cost = cost
        player.years = years

        if not self.Players._indexes["owner"].get(player.owner):
            self.Players._indexes["owner"][player.owner] = []
        insort_right(self.Players._indexes["owner"][player.owner], player)
        try:
            self.Players._indexes["owner"][None].remove(player)
        except:
            print(player.name)
            pass

    def remove_player_from_team(self, player, owner_name):
        remove_player.owner = None
        remove_player.cost = None
        remove_player.years = None

        if not self.Players._indexes["owner"].get(None):
            self.Players._indexes["owner"][None] = []
        insort_right(self.Players._indexes["owner"][None], player)
        self.Players._indexes["owner"][owner_name].remove(player)

    def add_redraft_data(self, player_name, tier, player_rank, player_bye):
        existing_player = self.fetch_player_by_name(player_name)

        if not existing_player:
            print("Player %s not in db" % player_name)
            return

        # map dyno value to redraft
        # _players should be sorted so this should be chill
        value = self.Players._players[(int(player_rank)-1)].value
        if value:
            existing_player.redraft_value = value

        if existing_player.redraft_tier != tier or existing_player.redraft_rank != player_rank:
            existing_player.redraft_rank = player_rank
            existing_player.redraft_tier = tier
            existing_player.bye = player_bye

    # GET METHODS PLAYERS
    def fetch_all_players(self, no_picks=True):
        if no_picks:
            return [player for player in self.Players._players if player.position != "PICK"]
        return self.Players._players

    def fetch_player_by_name(self, player_name):
        return self.Players._indexes["name"].get(player_name, None)

    def fetch_players_by_owner(self, owner_name):
        return self.Players._indexes["owner"].get(owner_name, [])

    def fetch_players_by_position(self, position):
        return self.Players._indexes["position"].get(position, [])

    def fetch_free_agents(self, no_picks=True, rookies=True):
        # TODO don't return rookies
        if no_picks:
            return [player for player in self.Players._players if (player.owner is None and player.position != "PICK")]
        return [player for player in self.Players._players if player.owner is None]

    # GET METHODS OWNERS
    def fetch_all_owners(self):
        return self.Owners._owners

    def fetch_owner_by_name(self, name):
        return self.Owners._indexes["name"].get(name)

    # LOAD FROM DICT
    def load_cache_from_dict(self, app_data):
        """
        Kind of confusing how this has to be done because of the crazy indexing thing i set up.
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
                "tier": <int>,
                "player_rank": <int>,
                "player_bye": <int>
            }, ...]
        }
        """
        assert app_data["players"]
        assert app_data["team_players"]
        assert app_data["owners"]
        assert app_data["redraft"]

        for player in app_data["players"]:
            self.new_player_value(**player)

        for team_player in app_data["team_players"]:
            player = self.fetch_player_by_name(team_player["player"])
            if not player:
                raise RuntimeError("Unable to load cache")
                return
            self.add_player_to_team(player=player,
                                    owner_name=team_player["owner_name"],
                                    cost=team_player["cost"],
                                    years=team_player["years"])

        for owner in app_data["owners"]:
            self.new_owner(**owner)

        for redraft_data in app_data["redraft"]:
            self.add_redraft_data(**redraft_data)


class Players:

    def __init__(self):
        self._indexes = {
            "name": {},
            "owner": {},
            "position": {}
        }
        self._players = []

    def __str__(self):
        return "Number of players in db %d" % len(self._players)

    def _add(self, player):
        insort_right(self._players, player)
        self._indexes["name"][player.name] = player

        if not self._indexes["owner"].get(player.owner):
            self._indexes["owner"][player.owner] = []
        insort_right(self._indexes["owner"][player.owner], player)

        if not self._indexes["position"].get(player.position):
            self._indexes["position"][player.position] = []
        insort_right(self._indexes["position"][player.position], player)

    def reindex_player(self, player):
        # FIXME yuck this is going to slow things down big time
        self._players.remove(player)
        self._indexes["position"][player.position].remove(player)
        self._indexes["owner"][player.owner].remove(player)

        insort_right(self._players, player)
        insort_right(self._indexes["owner"][player.owner], player)
        insort_right(self._indexes["position"][player.position], player)


class Player:

    def __init__(self,
                 name,
                 position,
                 value,
                 owner=None,
                 cost=None,
                 years=None,
                 redraft_rank=800,
                 redraft_tier=None,
                 bye=None,
                 redraft_value=None):
        self.name = name
        self.position = position
        self.value = int(value)
        self.owner = owner
        self.cost = cost
        self.years = years
        self.redraft_rank = redraft_rank
        self.redraft_tier = redraft_tier
        self.bye = bye
        self.redraft_value = redraft_value

    def __lt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def as_json(self):
        return {
            "name": self.name,
            "position": self.position,
            "value": int(self.value) if self.value else None,
            "owner": self.owner,
            "cost": int(self.cost) if self.cost else None,
            "years": int(self.years) if self.years else None,
            "redraft_rank": int(self.redraft_rank) if self.redraft_rank else None,
            "redraft_tier": int(self.redraft_tier) if self.redraft_tier else None,
            "bye": int(self.bye) if self.bye else None,
            "redraft_value": int(self.redraft_value) if self.redraft_value else None
        }


class Owners:

    def __init__(self):
        self._indexes = {
            "name": {},
        }
        self._owners = []

    def __str__(self):
        return "Number of owners in db %d" % len(self._owners)

    def _add(self, owner):
        self._owners.append(owner)
        self._indexes["name"][owner.name] = owner


class Owner:

    def __init__(self, name, cap_room=None, years_remaining=None, spots_available=None):
        self.name = name
        self.cap_room = cap_room
        self.years_remaining = years_remaining
        self.spots_available = spots_available

    def as_json(self):
        return {
            "name": self.name,
            "cap_room": int(self.cap_room) if self.cap_room else None,
            "years_remaining": int(self.years_remaining) if self.years_remaining else None,
            "spots_available": int(self.spots_available) if self.spots_available else None
        }
