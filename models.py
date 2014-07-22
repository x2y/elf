import re

from email.utils import parseaddr
from google.appengine.ext import ndb


NAME_KEY = 'name'
EMAIL_KEY = 'email'
GIVER_EMAIL_KEY = 'giverEmail'
RECEIVER_EMAIL_KEY = 'receiverEmail'
USERS_KEY = 'users'
POSITIVE_CONSTRAINTS_KEY = 'positiveConstraints'
NEGATIVE_CONSTRAINTS_KEY = 'negativeConstraints'
ASSIGNMENTS_KEY = 'assignments'


def validate_email(email):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        raise Exception('Invalid email: %s' % email)


class User(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=False)
    email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)

    def to_dict(self):
        return {
            NAME_KEY: self.name,
            EMAIL_KEY: self.email
        }


class Assignment(ndb.Model):
    giver_email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)
    receiver_email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)

    def to_dict(self):
        return {
            GIVER_EMAIL_KEY: self.giver_email,
            RECEIVER_EMAIL_KEY: self.receiver_email,
        }


class Party(ndb.Model):
    users = ndb.StructuredProperty(User, repeated=True)
    positive_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    negative_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    assignments = ndb.StructuredProperty(Assignment, repeated=True)

    def to_dict(self):
        return {
            USERS_KEY: [user.to_dict() for user in self.users],
            ASSIGNMENTS_KEY: [assignment.to_dict() for assignment in self.assignments],
        }
