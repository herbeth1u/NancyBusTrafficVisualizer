#!/usr/bin/env python
#

from Handler import Handler
from Ligne import Ligne

class Update(Handler):
    def get(self):
        Ligne.update_all()
        self.write("Done.")