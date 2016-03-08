#!/usr/bin/env python
#
import json

from Handler import Handler
from Bus1 import Bus1
from Route1 import Route1


class Data(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        res = []
        for bus in Bus1.find_all():
            res.append(bus.toJSON())
        for route in Route1.find_all():
            res.append(route.toJSON())
        circles = [{
                       "id": 1,
                       "type": "circle",
                       "name": "circle",
                       "x": 43.604482,
                       "y": 1.443962,
                       "radius": 10*1000,
                       "fillOpacity": 0.4,
                       "metadata": ["Rayon 1"]
                   }, {
                       "id": 2,
                       "type": "circle",
                       "name": "circle",
                       "x": 45.783088,
                       "y": 3.082352,
                       "radius": 40*1000,
                       "fillOpacity": 0.4,
                       "metadata": ["Rayon 2"]
                   }]
        for circle in circles:
            res.append(circle)
        self.write(json.dumps(res))