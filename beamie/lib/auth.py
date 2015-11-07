#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import logging as log

from beamie.lib.tokens import do_validate_token

class Authenticated(object):
    """A decorator to handle auth for us"""

    def __init__(self, allowed_roles=[], strict=False):
        self.allowed_roles = allowed_roles
        self.strict = strict

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            req = flask.request
            log.debug("Handling %s to %s" % (
                req.method, req.path ) )

            # Try to get the user's roles
            try:
                token_data = do_validate_token(req.headers['x-auth-token'])
            except KeyError:
                flask.abort(401)
                return

            log.debug("Token data: %s" % token_data)

            if token_data is None or token_data is False:
                flask.abort(401)
                return

            # This might be false for a variety of reasons, all of which amount to
            # failed auth in some form.
            if len(token_data['user']['roles']) < 1:
                log.debug("Aborting request due to bad role check")
                flask.abort(401)
                return

            # If the user is disabled, fail, even if other roles are present
            if 'disabled' in token_data['user']['roles']:
                log.debug("User is disabled")
                flask.abort(401)
                return

            # We're given a list of allowed roles. If "strict" is on, the user must
            # be in all roles (AND). If not, the user must be in at least one role (OR).
            if self.strict:
                allowed = True
                for role in token_data['user']['roles']:
                    if role not in self.allowed_roles:
                        allowed = False
                        break
                if not allowed:
                    log.debug("User is not allowed!")
                    flask.abort(401)
                    return
            else:
                allowed = False
                for role in token_data['user']['roles']:
                    log.debug("Comparing user role %s against allowed roles %s" % (
                        role, self.allowed_roles ) )
                    if role in self.allowed_roles:
                        log.debug("User is allowed!")
                        allowed = True
                        break
                if not allowed:
                    log.debug("User not allowed!")
                    flask.abort(401)
                    return

            return f(*args, **kwargs)

        return wrapped_f

