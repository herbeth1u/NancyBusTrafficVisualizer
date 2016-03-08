#!/usr/bin/env python
# encoding:Utf-8
import json
import time

from Handler import Handler
from nancy.JSONFile import JSONFile
from nancy.Bus import Bus
import DBKey

REFRESH = 10


class Data(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        json_file = 'files/sae_json.txt'

        # récupérer, à partir du gros JSON stocké sur le serveur, l'état actuel = l'objet JSON qui commence à la ligne
        # indiquée par JSONFile::current_line dans la BDD
        # Cet algo marche sur un JSON beautified ou non
        current = JSONFile.get_current()
        if current is None:
            current = JSONFile(parent=DBKey.key())
            current.put()
            current_pos = 0
        else:
            current_pos = current.current_pos
            timestamp = current.timestamp
            if abs(timestamp - time.time()) < REFRESH:
                last_state = eval(current.last_state)
                self.write(json.dumps(last_state))
                return

        f = self.next_file(json_file, current)
        f.seek(current_pos, 0)

        is_new_object = True
        json_string = ""
        while True:
            c = f.read(1)
            json_string += c

            # si on est au bout, on revient au début (pas réaliste mais évite la pénurie de données)
            if c.isspace():
                continue
            elif not c or c == "":
                # Fin de fichier : on passe au suivant
                json_string = ""
                current.current_file += 1
                f = self.next_file(json_file, current)
                continue
            elif c == '{' and is_new_object:
                is_new_object = False
            elif c == ']' and not is_new_object:
                is_new_object = True
            elif c == '}' and is_new_object:
                break

        # mettre à jour la BDD avec le nouvel état (liste des bus + JSONFile::current_pos)
        # j = JSONFile.get_current()
        current.current_pos = f.tell()
        current.timestamp = time.time()

        try:
            liste_bus = json.loads(json_string)
        except ValueError:
            current.current_file = 1
            current.current_pos = 0
            current.put()
            return

        res = []
        res.append({"type": "date", "date": liste_bus['date'], "time": liste_bus["time"]})
        for bus in liste_bus['bus']:
            gps = bus['gps'].split(',')
            bus = Bus(no_parc=bus['no_parc'], type_vehicule=bus['type_vehicule'], ligne=bus['ligne'],
                      service=bus['service'],
                      rang_course=bus['rang_course'], chainage=bus['chainage'], distance=bus['distance'],
                      position=bus['position'],
                      anomalie=bus['anomalie'], avance_retard=bus['avance_retard'], lat=float(gps[0]),
                      lng=float(gps[1]),
                      parent=DBKey.key())

            if bus.lat > 1 and bus.lng > 1:
                res.append(bus.toJSON())

        current.last_state = str(res)
        current.put()
        self.write(json.dumps(res))

    def next_file(self, json_file, current):
        try:
            f = open(json_file + str(current.current_file))
        except IOError:
            current.current_file = 1
            try:
                f = open(json_file + str(current.current_file))
            except IOError:
                last_state = eval(current.last_state)
                self.write(json.dumps(last_state))
                return
        return f