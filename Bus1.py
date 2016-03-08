from random import random
from google.appengine.ext import db
from Handler import Handler


class Bus1(db.Model):
    id = db.IntegerProperty(required=True)
    type = db.StringProperty(required=True, default="object")
    name = db.StringProperty(required=True, default="bus")
    x = db.FloatProperty(required=True)
    y = db.FloatProperty(required=True)
    breakdown = db.BooleanProperty(required=True, default=False)

    def toJSON(self):
        d = {}
        d["id"] = self.id
        d["type"] = self.type
        d["name"] = self.name
        d["x"] = self.x
        d["y"] = self.y
        d["breakdown"] = self.breakdown
        return d

    @staticmethod
    def find_all():
        bus = db.GqlQuery("SELECT * FROM Bus1 WHERE ANCESTOR IS :1", Handler.db_key())
        return list(bus)

    @staticmethod
    def maxid():
        l = [b.id for b in Bus1.find_all()]
        if len(l) < 1:
            return 0
        return max(l)

    def move(self):
        randomLat = random() / 10000
        randomLng = random() / 10000
        randomLatSide = random()
        randomLngSide = random()
        randomBreakdown = random()

        if randomLatSide > 0.5:
            self.x += randomLat
        else:
            self.x -= randomLat
        if randomLngSide > 0.5:
            self.y += randomLng
        else:
            self.y -= randomLng
        if randomBreakdown > 0.5:
            self.breakdown = True
        else:
            self.breakdown = False