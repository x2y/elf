import webapp2

from handlers import *
from models import *


GROUP_ID_REGEX = r'([a-zA-Z0-9_-]{11})'

app = webapp2.WSGIApplication([
    # HTML handlers.
    (r'^/$', IndexHandler),
    (r'^/create/$', CreateGroupHandler),
    (r'^/open/$', OpenGroupHandler),
    (r'^/build/%s/$' % GROUP_ID_REGEX, BuildGroupHandler),
    (r'^/join/%s/$' % GROUP_ID_REGEX, JoinGroupHandler),
    (r'^/tweak/%s/$' % GROUP_ID_REGEX, TweakGroupHandler),
    (r'^/review/%s/$' % GROUP_ID_REGEX, ReviewAssignmentsHandler),
    (r'^/done/%s/$' % GROUP_ID_REGEX, AssignmentsSentHandler),
    # AJAX handlers.
    (r'^/x/create-group/$', AjaxCreateGroupHandler),
    # AppEngine handlers.
    (r'^/_ah/warmup$', WarmupHandler),
], debug=True)
