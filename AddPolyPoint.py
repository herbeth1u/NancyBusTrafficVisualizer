#!/usr/bin/env python
#

from Handler import Handler
import random
from Route1 import Route1


class AddPolyPoint(Handler):
    def get(self):
        for route in Route1.find_all():
            randomLat = random.uniform(43.296346, 50.637222)
            randomLng = random.uniform(-4.485556, 7.750576)
            route.addPoint(x=randomLat, y=randomLng)
            route.put()

        self.write("Done.")