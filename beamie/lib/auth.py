#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import hashlib
import logging as log

import beamie.data as data
from beamie.lib.tokens import generate_token, validate_token

DEFAULT_HEADERS = { "Content-Type" : "application/json" }

class Authorized(object):
    """A decorator to handle authorization for us"""

    def __init__(self, allowed_roles=[], strict=False):
        """Create a new Authorized function.
           
           Parameters:
             - allowed_roles: List of role names allowed to call this function
             - strict: bool
               - False (default): User must be in any one of the given roles
               - True: User must be in all of the given roles
        """

        self.allowed_roles = allowed_roles
        self.strict = strict

    def __call__(self, f):
        """Calls the intended function only if the user is authorized."""

        def wrapped_f(*args, **kwargs):
            req = flask.request
            log.debug("Authorizing call to %s to %s" % (
                req.method, req.path ) )

            # Try to get the user's roles
            try:
                token_data = validate_token(req.headers['x-auth-token'])
            except KeyError:
                return flask.make_response('', 401)

            log.debug("Token data: %s" % token_data)

            if token_data is None or token_data is False:
                return flask.make_response('', 401)

            if len(token_data['user']['roles']) < 1:
                return flask.make_response(
                    json.dumps({
                        'error' : 'User is not a member of any roles'
                    }),
                    401,
                    DEFAULT_HEADERS
                )

            if 'disabled' in token_data['user']['roles']:
                return flask.make_response('', 401)

            if self.strict:
                allowed = True
                for role in self.allowed_roles:
                    if role not in token_data['user']['roles']:
                        allowed = False
                        break
                if not allowed:
                    log.debug("User is not allowed!")
                    return flask.make_response('', 401)
            else:
                allowed = False
                for role in token_data['user']['roles']:
                    if role in self.allowed_roles:
                        allowed = True
                        break
                if not allowed:
                    log.debug("User not allowed!")
                    return flask.make_response('', 401)

            return f(*args, **kwargs)

        return wrapped_f


def authenticate(user, passwd):
    """Authenticate a user and generate a token.

       Returns:
         - False: Auth failed (password mismatch or disabled account)
         - None: Invalid username
         - Token ID: Success
    """
    session = data.session()
 
    # Get user by name. No user match? return None
    users = session.query(data.User).filter_by(username=user)
    if users.count() >= 1:
        user = users.first()
        memberships = session.query(data.RoleMembership).filter_by(user_id=user.id)
        if 'disabled' in [ membership.role.name for membership in memberships ]:
            return False
        else:
            inputhash = hashlib.sha512("".join([passwd, user.salt])).hexdigest()
            if inputhash == user.pwhash:
                return generate_token(user)
            else:
                return False
    else:
        return None

