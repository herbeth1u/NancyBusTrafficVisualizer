#!/usr/bin/env python
#
import os
from google.appengine.ext import db
import webapp2
import jinja2
import hashlib

SECRET = "kOlV6MHDa3vzdpmh7thA"

class Handler(webapp2.RequestHandler):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = self.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def hash(self, value):
        return str("%s|%s" % (value, hashlib.sha256(SECRET + value).hexdigest()))

    def add_cookie(self, name, value):
        cookie = self.hash(value)
        self.response.headers.add_header('Set-Cookie', "%s=%s; Path=/" % (name, cookie))

    def check_cookie(self):
        username_cookie = self.request.cookies.get('username')
        if username_cookie == None:
            return None
        username = username_cookie.split('|')[0]
        if username_cookie != self.hash(username):
            return None
        return username

    @staticmethod
    def db_key(name='default'):
        return db.Key.from_path('wiki', name)