import jinja2
import json
import logging
import os
import traceback
import webapp2

from functools import wraps
from google.appengine.api import memcache
from google.appengine.ext import ndb
from models import *
from urllib import urlencode


TEMPLATE_KEY = 'template'
ERRORS_KEY = 'errors'


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.filters.update({'urlencode': lambda s: urlencode({'': s.encode('utf8')})[1:]})


def rate_limit(seconds_per_request=1):
    def rate_limiter(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            added = memcache.add(
                '%s:%s' % (self.__class__.__name__, self.request.remote_addr or ''), 1,
                time=seconds_per_request, namespace='rate_limiting')
            if not added:
                self.response.write('Rate limit exceeded.')
                self.response.set_status(403)
                return
            return function(self, *args, **kwargs)
        return wrapper
    return rate_limiter


def render_to(template=''):
    def renderer(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            output = function(self, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop(TEMPLATE_KEY, template)
            self.response.write(JINJA_ENVIRONMENT.get_template(tmpl).render(output))
        return wrapper
    return renderer


def json_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, ndb.Model):
        return obj.to_dict()
    else:
        raise TypeError("%r is not JSON serializable" % obj)


def to_json(value):
    return json.dumps(value, default=json_handler)
JINJA_ENVIRONMENT.filters.update({'to_json': lambda obj: jinja2.Markup(to_json(obj))})


def ajax_request(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            output = function(self, *args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
            output = {ERRORS_KEY: 'Unexpected exception! %s: %s' % (e.__class__.__name__, e)}
        data = to_json(output)
        self.response.content_type = 'application/json'
        self.response.write(data)
    return wrapper


class WarmupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=10)
    def get(self):
        self.response.write('Warmed up!')


class IndexHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=1)
    @render_to('index.html')
    def get(self):
        return {}


class CreateGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('create_group.html')
    def get(self):
        return {}


class OpenGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('open_group.html')
    def get(self):
        return {}


class BuildGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('build_group.html')
    def get(self, group_id):
        return {}


class JoinGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('join_group.html')
    def get(self, group_id):
        return {}


class TweakGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('tweak_group.html')
    def get(self, group_id):
        return {}


class ReviewAssignmentsHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('review_assignments.html')
    def get(self, group_id):
        return {}


class AssignmentsSentHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('assignments_sent.html')
    def get(self, group_id):
        return {}
