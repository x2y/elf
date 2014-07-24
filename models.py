import base64
import random
import re
import struct

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


def generate_id():
    """Generate a (theoretically globally unique) random 64-bit id encoded as a base64 string.

    Returns:
        A new random string id matching the regex r'([a-zA-Z0-9_=-]+){11}'.
    """
    numeric_id = random.getrandbits(64) - 2 ** 63
    return base64.urlsafe_b64encode(struct.pack('q', numeric_id))[:-1]


def validate_name(name):
    """Validate the specified name, throwing an exception if invalid.

    Args:
        name: The name to validate.

    Raises:
        Exception: If the name is too long.
    """
    if len(name) > 100:
        raise Exception('Name is too long!')


def validate_email(email):
    """Validate the specified email, throwing an exception if invalid.

    Args:
        email: The email to validate.

    Raises:
        Exception: If the email does not match a basic email format.
    """
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        raise Exception('Invalid email: %s!' % email)


class User(ndb.Model):
    """A single immutable user model."""

    name = ndb.StringProperty(required=True, indexed=False, validator=validate_name)
    email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)

    def to_dict(self):
        """Convert the user to an easily-serializable dict."""
        return {
            NAME_KEY: self.name,
            EMAIL_KEY: self.email
        }


class Assignment(ndb.Model):
    """A model assigning one user to another, as identified by their email addresses."""

    giver_email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)
    receiver_email = ndb.StringProperty(required=True, indexed=False, validator=validate_email)

    def to_dict(self):
        """Convert the assignment to an easily-serializable dict."""
        return {
            GIVER_EMAIL_KEY: self.giver_email,
            RECEIVER_EMAIL_KEY: self.receiver_email,
        }


class Group(ndb.Model):
    """A model for a single group of users, their constraints, and their assignments."""

    name = ndb.StringProperty(required=True, indexed=False, validator=validate_name)
    users = ndb.StructuredProperty(User, repeated=True)
    positive_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    negative_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    assignments = ndb.StructuredProperty(Assignment, repeated=True)

    def to_dict(self):
        """Convert the group to an easily-serializable dict."""
        return {
            NAME_KEY: self.name,
            USERS_KEY: [user.to_dict() for user in self.users],
            ASSIGNMENTS_KEY: [assignment.to_dict() for assignment in self.assignments],
        }
