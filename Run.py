#!/usr/bin/env python
#
import time

from Handler import Handler
from Bus1 import Bus1


class Run(Handler):
    TIME = 1000

    def get(self):
        for  i in range(self.TIME):
            for bus in Bus1.find_all():
                bus.move()
                bus.put()
            time.sleep(0.5)

        self.write("Done.")