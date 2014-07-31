import datetime
import jinja2
import json
import logging
import os
import time
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
        return to_timestamp(obj)
    elif isinstance(obj, ndb.Model):
        return obj.to_dict()
    else:
        raise TypeError("%r is not JSON serializable" % obj)


def to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))


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
    def get(self, key):
        return {
            KEY_KEY: key
        }


class JoinGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('join_group.html')
    def get(self, key):
        return {}


class TweakGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('tweak_group.html')
    def get(self, key):
        return {}


class ReviewAssignmentsHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('review_assignments.html')
    def get(self, key):
        return {}


class AssignmentsSentHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @render_to('assignments_sent.html')
    def get(self, key):
        return {}


class AjaxCreateGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=2)
    @ajax_request
    def post(self):
        name = self.request.POST[NAME_KEY].strip()
        if not name:
            return {ERRORS_KEY: 'We\'re gonna need a name for your group.'}

        admin_email = self.request.POST[ADMIN_EMAIL_KEY].strip()
        if not admin_email:
            return {ERRORS_KEY: 'We\'re gonna need an email for your group\'s coordinator.'}

        try:
            group = Group(key=ndb.Key(Group, generate_id()), name=name, admin_email=admin_email)
            group.put()
        except Exception as e:
            return {ERRORS_KEY: e.message}

        return group.to_dict()


class AjaxGetGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=1)
    @ajax_request
    def get(self):
        group = ndb.Key(Group, self.request.GET[KEY_KEY]).get()
        if not group:
            return {ERRORS_KEY: 'Hmm. We don\'t recognize that group.'}
        return group.to_dict()


class AjaxUpdateGroupHandler(webapp2.RequestHandler):
    @rate_limit(seconds_per_request=1)
    @ajax_request
    def post(self):
        # Load the Group.
        group = ndb.Key(Group, self.request.POST[KEY_KEY]).get()
        if not group:
            return {ERRORS_KEY: 'Hmm. We don\'t recognize that group.'}

        # Validate the operation.
        if group.assignments:
            return {ERRORS_KEY: 'I\'m sorry. You can\'t change a group\'s members after their ' +
                                'assignments have been made.'}

        # Validate the version.
        try:
            version = int(self.request.POST[VERSION_KEY])
        except:
            return {ERRORS_KEY: 'That\'s not a valid version.'}

        if version != to_timestamp(group.version):
            return {ERRORS_KEY: 'Looks like someone\'s joined the group since this you\'ve made ' +
                                'changes. Refresh the page to load the latest members.'}

        # Validate/build the user list.
        try:
            users = json.loads(self.request.POST.get(USERS_KEY))
        except:
            return {ERRORS_KEY: 'The members list is not in a valid format.'}

        group.users = []
        for user in users:
            name, email = user[NAME_KEY].strip(), user[EMAIL_KEY].strip()
            if not name and not email:
                continue

            try:
                group.users.append(User(name=name, email=email))
            except Exception as e:
                return {ERRORS_KEY: e.message}

        try:
            group.put()
        except Exception as e:
            return {ERRORS_KEY: e.message}

        return group.to_dict()
