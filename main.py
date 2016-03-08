#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from Handler import Handler
from Data import Data
from Init import Init
from Run import Run
from Put import Put
from AddPolyPoint import AddPolyPoint
from nancy.Init import Init as NancyInit
from nancy.Data import Data as NancyData
from nancy.Update import Update as NancyUpdate

class MainHandler(Handler):
    def get(self):
        self.render('home.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/data', Data),
    ('/init', Init),
    ('/run', Run),
    ('/put', Put),
    ('/add_poly_point', AddPolyPoint),
    ('/nancy/init', NancyInit),
    ('/nancy/data', NancyData),
    ('/nancy/update', NancyUpdate)
], debug=True)
