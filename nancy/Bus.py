#!/usr/bin/env python
# encoding:Utf-8
from google.appengine.ext import db

import DBKey


class Bus(db.Model):
    type = db.StringProperty(required=True, default="object")
    type_vehicule = db.StringProperty(required=True)
    no_parc = db.StringProperty(required=True)
    ligne = db.StringProperty(required=True)
    service = db.StringProperty(required=True)
    rang_course = db.StringProperty(required=True)
    chainage = db.StringProperty()
    distance = db.StringProperty(required=True)
    position = db.StringProperty(required=True)
    anomalie = db.StringProperty(required=True)
    avance_retard = db.StringProperty(required=True)

    lat = db.FloatProperty(required=True)
    lng = db.FloatProperty(required=True)

    def toJSON(self):
        d = {}
        d["id"] = self.no_parc
        d["type"] = self.type
        d["name"] = self.type_vehicule
        d["x"] = self.lat
        d["y"] = self.lng
        d["anomalie"] = self.anomalie
        d["label"] = "Ligne " + str(self.ligne)

        metadata = []
        metadata.append("Type véhicule : " + str(self.type_vehicule))
        metadata.append("N° parc : " + str(self.no_parc))
        metadata.append("Position : " + str(self.lat) + " ; " + str(self.lng))
        metadata.append("Ligne " + str(self.ligne))
        metadata.append("Service " + str(self.service))
        metadata.append("Rang " + str(self.rang_course))
        metadata.append("Chainage " + str(self.chainage))
        metadata.append("Distance parcourue : " + str(self.distance))
        metadata.append("Position : " + str(self.position))
        metadata.append("Avance : " + str(self.avance_retard))
        d["metadata"] = metadata
        return d

    @staticmethod
    def find_all():
        bus = db.GqlQuery("SELECT * FROM Bus WHERE ANCESTOR IS :1", DBKey.key())
        return list(bus)

    @staticmethod
    def find_by_id(id):
        bus = db.GqlQuery("SELECT * FROM Bus WHERE ANCESTOR IS :1 AND no_parc = :2", DBKey.key(), id)
        bus = list(bus)
        if len(bus) < 1:
            return None
        return bus[0]