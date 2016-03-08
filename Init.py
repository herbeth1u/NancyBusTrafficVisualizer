#!/usr/bin/env python
#
import json
import socket

from Handler import Handler


class Init(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        path = socket.gethostname()

        d = {
            "initZoom": 6,
            "initLat": 46.856578,
            "initLng": 2.351828,
            "images" : {
                "bus": {
                    "default": path + "/images/bus_small.png",
                    "breakdown": path + "/images/bus_anomalie.png"
                }
            },
            "objects": [{
                "x": 48.390834,
                "y": -4.485556,
                "image": path + "/images/bus_anomalie.png",
                "metadata": ["Bus statique 1"]
            }, {
                "x": 48.114722,
                "y": -1.679444,
                "image": path + "/images/bus_anomalie.png",
                "metadata": ["Bus statique 2"]
            }],
            "circles": [{
                "x": 43.296346,
                "y": 5.369889,
                "radius": 30*1000,
                "fillColor": 'yellow',
                "fillOpacity": 0.4,
                "color": 'yellow',
                "metadata": ["Rayon statique 1"]
            }]
        }
        self.write(json.dumps(d))