from config import config
from webapp.db import db


class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.Enum('QB', 'RB', 'WR', 'TE', 'PICK', name='positions'), nullable=False)
    value = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=True)
    owner = db.relationship('Owners', foreign_keys=owner_id)
    cost = db.Column(db.Integer)
    years = db.Column(db.Integer)
    redraft_rank = db.Column(db.Integer)
    redraft_tier = db.Column(db.Integer)
    bye = db.Column(db.Integer)
    # TODO take this out and use custom formula based off of rank and tier
    redraft_value = db.Column(db.Integer)


    def __init__(self, name, position, value, owner=None, cost=None, years=None, redraft_rank=800, redraft_tier=None, bye=None, redraft_value=None):
        self.name = name
        self.position = position
        self.value = value
        self.owner = owner
        self.cost = cost
        self.years = years
        self.redraft_rank = redraft_rank
        self.redraft_tier = redraft_tier
        self.bye = bye
        self.redraft_value = redraft_value

    @classmethod
    def new_player_value(cls, name, position, value):
        existing_player = cls.query.filter_by(name=name).first()

        if existing_player and value != existing_player.value:
            existing_player.value = value
            db.session.add(existing_player)
        elif not existing_player:
            new_player = cls(name, position, value)
            db.session.add(new_player)

        db.session.commit()

    @classmethod
    def add_redraft_data(cls, name, tier, rank, bye):
        existing_player = cls.query.filter_by(name=name).first()

        if not existing_player:
            print("Player %s not in db" % name)
            return

        # map dyno value to redraft
        # NOTE values could have still changed even if rank doesn't change so we have to check every time
        value = Players.query.order_by(Players.value.desc()).offset((int(rank)-1)).limit(1).first().value
        if value:
            existing_player.redraft_value = value

        if existing_player.redraft_tier != tier or existing_player.redraft_rank != rank:
            existing_player.redraft_rank = rank
            existing_player.redraft_tier = tier
            existing_player.bye = bye

            db.session.add(existing_player)

            db.session.commit()

    def as_json(self):
        return {
            "name": self.name,
            "position": self.position,
            "value": self.value,
            "owner": self.owner.name if self.owner else None,
            "cost": self.cost,
            "years": self.years,
            "redraft_rank": self.redraft_rank,
            "redraft_tier": self.redraft_tier,
            "bye": self.bye,
            "redraft_value": self.redraft_value,
        }


class Owners(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    cap_room = db.Column(db.Integer)
    years_remaining = db.Column(db.Integer)
    spots_available = db.Column(db.Integer)


    def __init__(self, name, cap_room=None, years_remaining=None, spots_available=None):
        self.name = name
        self.cap_room = cap_room
        self.years_remaining = years_remaining
        self.spots_available = spots_available

    def as_json(self):
        return {
            "name": self.name,
            "cap_room": self.cap_room,
            "years_remaining": self.years_remaining,
            "spots_available": self.spots_available
        }
