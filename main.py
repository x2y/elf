import webapp2

from handlers import *
from models import *


app = webapp2.WSGIApplication([
    (r'^/$', IndexHandler),
    (r'^/_ah/warmup$', WarmupHandler),
], debug=True)
