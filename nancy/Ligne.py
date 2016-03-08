#!/usr/bin/env python
# encoding:Utf-8
from google.appengine.ext import db

import DBKey
from xml.dom import minidom


class Ligne(db.Model):
    name = db.StringProperty(required=True)
    points = db.TextProperty(required=True)
    sens = db.StringProperty(required=True)
    color = db.StringProperty(required=True, default='blue')

    def toJSON(self):
        d = {}
        d['color'] = self.color
        d['opacity'] = 0.2
        d['points'] = []
        for point in str(self.points).split(' '):
            if len(point) < 1: continue
            d['points'].append({'x': float(point.split(',')[1]), 'y': float(point.split(',')[0])})
        d['metadata'] = [self.name, "Sens : " + str(self.sens)]
        return d

    @staticmethod
    def find_all():
        lignes = db.GqlQuery("SELECT * FROM Ligne WHERE ANCESTOR IS :1", DBKey.key())
        return list(lignes)

    @staticmethod
    def find_by_name(name):
        lignes = db.GqlQuery("SELECT * FROM Ligne WHERE ANCESTOR IS :1 AND name = :2", DBKey.key(), name)
        lignes = list(lignes)
        if len(lignes) < 1:
            return None
        return lignes[0]

    @staticmethod
    def update_all():
        with open('files/Lignes_bus.kml') as f:
            query = minidom.parseString(f.read())
            folders = query.getElementsByTagName('folder')

            # boucler sur les folder , pour chaque folder getelementbyname (name) , placemark ,  getelementbyname(coordinates)
            for folder in folders:
                name = folder.getElementsByTagName('name')[0].firstChild.nodeValue
                points = folder.getElementsByTagName('coordinates')[0].firstChild.nodeValue
                sens = [e.firstChild.nodeValue for e in folder.getElementsByTagName('simpledata') if e.getAttribute('name') == 'SENS']
                sens = sens[0] if len(sens) > 0 else 'Aller - Retour'
                color = 'blue' if sens == 'Aller' else 'red' if sens == 'Retour' else 'green'

                ligne = Ligne.find_by_name(name)
                if ligne is None:
                    Ligne(name=name, points=points, sens=sens, color=color, parent=DBKey.key()).put()
                else:
                    ligne.points = points
                    ligne.sens = sens
                    ligne.color = color
                    ligne.put()