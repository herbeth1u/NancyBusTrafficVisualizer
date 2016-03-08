from google.appengine.ext import db

import DBKey
import logging
import time

class JSONFile(db.Model):
    current_file = db.IntegerProperty(required=True, default=1)
    current_pos = db.IntegerProperty(required=True, default=0)
    timestamp = db.FloatProperty(required=True, default=time.time())
    last_state = db.TextProperty(required=True, default="[]")

    @staticmethod
    def get_current():
        file = db.GqlQuery("SELECT * FROM JSONFile WHERE ANCESTOR IS :1", DBKey.key())
        file = list(file)
        if len(file) < 1:
            return None
        return file[0]