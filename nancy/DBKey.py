#!/usr/bin/env python
# encoding:Utf-8
#
from google.appengine.ext import db

def key():
    return db.Key.from_path('pidr_nancy', 'default')