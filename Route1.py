from google.appengine.ext import db
from Handler import Handler
import logging

class Route1(db.Model):
    id = db.IntegerProperty(required=True)
    type = db.StringProperty(required=True, default="polyline")
    name = db.StringProperty(required=True, default="route")
    points = db.TextProperty(default="[]")
    color = db.StringProperty(required=True, default="blue")

    def toJSON(self):
        d = {}
        d["id"] = self.id
        d["type"] = self.type
        d["name"] = self.name
        d["color"] = self.color
        d["points"] = eval(self.points)
        return d

    @staticmethod
    def find_all():
        bus = db.GqlQuery("SELECT * FROM Route1 WHERE ANCESTOR IS :1", Handler.db_key())
        return list(bus)

    @staticmethod
    def find_by_id(id):
        poly = db.GqlQuery("SELECT * FROM Route1 WHERE ANCESTOR IS :1 AND id = :2", Handler.db_key(), id)
        poly = list(poly)
        if len(poly) < 1:
            return None
        logging.error(poly[0].points)
        return poly[0]

    @staticmethod
    def maxid():
        l = [b.id for b in Route1.find_all()]
        if len(l) < 1:
            return 0
        return max(l)

    def addPoint(self, x, y):
        p = eval(self.points)
        p.append({"x": x, "y": y})
        self.points = str(p)