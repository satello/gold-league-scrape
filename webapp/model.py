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


    def __init__(self, name, position, value, owner=None, cost=None, years=None):
        self.name = name
        self.position = position
        self.value = value
        self.owner = owner
        self.cost = cost
        self.years = years

    @classmethod
    def new_player_value(cls, name, position, value):
        existing_player = cls.query.filter_by(name=name).first()

        # adjust by weight
        value += int(value * config["weights"][position])

        if existing_player and value != existing_player.value:
            existing_player.value = value
            db.session.add(existing_player)
        elif not existing_player:
            new_player = cls(name, position, value)
            db.session.add(new_player)

        db.session.commit()

    def as_json(self):
        return {
            "name": self.name,
            "position": self.position,
            "value": self.value,
            "owner": self.owner.name,
            "cost": self.cost,
            "years": self.years
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
