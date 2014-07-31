import webapp2

from handlers import *
from models import *


GROUP_KEY_REGEX = r'([a-zA-Z0-9_-]{11})'

app = webapp2.WSGIApplication([
    # HTML handlers.
    (r'^/$', IndexHandler),
    (r'^/create/$', CreateGroupHandler),
    (r'^/open/$', OpenGroupHandler),
    (r'^/build/%s/$' % GROUP_KEY_REGEX, BuildGroupHandler),
    (r'^/join/%s/$' % GROUP_KEY_REGEX, JoinGroupHandler),
    (r'^/tweak/%s/$' % GROUP_KEY_REGEX, TweakGroupHandler),
    (r'^/review/%s/$' % GROUP_KEY_REGEX, ReviewAssignmentsHandler),
    (r'^/done/%s/$' % GROUP_KEY_REGEX, AssignmentsSentHandler),
    # AJAX handlers.
    (r'^/x/create-group/$', AjaxCreateGroupHandler),
    (r'^/x/get-group/$', AjaxGetGroupHandler),
    (r'^/x/update-group/$', AjaxUpdateGroupHandler),
    # AppEngine handlers.
    (r'^/_ah/warmup$', WarmupHandler),
], debug=True)
