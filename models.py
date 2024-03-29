import base64
import random
import re
import struct

from email.utils import parseaddr
from google.appengine.ext import ndb


ADMIN_EMAIL_KEY = 'adminEmail'
ASSIGNMENTS_KEY = 'assignments'
EMAIL_KEY = 'email'
GIVER_EMAIL_KEY = 'giverEmail'
KEY_KEY = 'key'
NAME_KEY = 'name'
NEGATIVE_CONSTRAINTS_KEY = 'negativeConstraints'
POSITIVE_CONSTRAINTS_KEY = 'positiveConstraints'
RECEIVER_EMAIL_KEY = 'receiverEmail'
USERS_KEY = 'users'
VERSION_KEY = 'version'


def generate_id():
    """Generate a (theoretically globally unique) random 64-bit id encoded as a base64 string.

    Returns:
        A new random string id matching the regex r'([a-zA-Z0-9_=-]+){11}'.
    """
    numeric_id = random.getrandbits(64) - 2 ** 63
    return base64.urlsafe_b64encode(struct.pack('q', numeric_id))[:-1]


def validate_name(property, name):
    """Validate the specified name, throwing an exception if invalid.

    Args:
        property: The property being validated.
        name: The name to validate.

    Raises:
        Exception: If the name is too long.
    """
    if not name:
        raise Exception('Uh-oh. You forgot a name!')
    elif len(name) > 128:
        raise Exception('Uh-oh. That name is too long!')


def validate_email(property, email):
    """Validate the specified email, throwing an exception if invalid.

    Args:
        property: The property being validated.
        email: The email to validate.

    Raises:
        Exception: If the email does not match a basic email format.
    """
    if not email:
        raise Exception('Uh-oh. You forgot an email!')
    elif len(email) > 128:
        raise Exception('Uh-oh. That email is too long!')
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        raise Exception('%s is not a valid email address.' % email)


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
    admin_email = ndb.StringProperty(required=True, indexed=True, validator=validate_email)
    version = ndb.DateTimeProperty(required=True, indexed=False, auto_now=True)
    users = ndb.StructuredProperty(User, repeated=True)
    positive_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    negative_constraints = ndb.StructuredProperty(Assignment, repeated=True)
    assignments = ndb.StructuredProperty(Assignment, repeated=True)

    def _pre_put_hook(self):
        names, emails = set(), set()
        for user in self.users:
            if user.name.lower() in names:
                raise Exception('More than one member has the name "%s".' % user.name)
            names.add(user.name.lower())

    def to_dict(self):
        """Convert the group to an easily-serializable dict."""
        return {
            KEY_KEY: self.key.id(),
            NAME_KEY: self.name,
            VERSION_KEY: self.version,
            USERS_KEY: [user.to_dict() for user in self.users],
            ASSIGNMENTS_KEY: [assignment.to_dict() for assignment in self.assignments],
        }
