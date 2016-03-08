#!/usr/bin/env python
#

from Handler import Handler
from Bus1 import Bus1
from Route1 import Route1


class Put(Handler):
    def get(self):
        NANCY = (48.70, 6.20)
        PARIS = (48.856578, 2.351828)
        BORDEAUX = (44.837912, -0.579541)

        id = Bus1.maxid()
        Bus1(x=NANCY[0], y=NANCY[1], id=id + 1, parent=Handler.db_key()).put()
        Bus1(x=PARIS[0], y=PARIS[1], id=id + 2, parent=Handler.db_key()).put()

        id = Route1.maxid()
        p = Route1(id=id + 1, parent=Handler.db_key())
        p.addPoint(x=NANCY[0], y=NANCY[1])
        p.addPoint(x=PARIS[0], y=PARIS[1])
        p.put()

        p = Route1(id=id + 2, color="red", parent=Handler.db_key())
        p.addPoint(x=NANCY[0], y=NANCY[1])
        p.addPoint(x=BORDEAUX[0], y=BORDEAUX[1])
        p.put()

        self.write("Done.")