#!/usr/bin/env python
#

import json
import socket

from Handler import Handler
import logging
from Ligne import Ligne


class Init(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        path = "http://" + socket.gethostname()

        polylines = []
        for ligne in Ligne.find_all():
            polylines.append(ligne.toJSON())

        d = {
            "initZoom": 12,
            "initLat": 48.68,
            "initLng": 6.20,
            "images": {
                "GX317-G": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "CITARO": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "CITELIS": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "GX417-G": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "CREALIS": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "MINIBUS": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "TRAMWAY": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                },
                "GX217-G": {
                    "default": path + "/images/bus_small.png",
                    "anomalie": path + "/images/bus_anomalie.png"
                }
            },
            "polylines": polylines
        }

        self.write(json.dumps(d))