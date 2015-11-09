#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Global modules
import flask
import hashlib
import logging as log
import math
import random
import time

from time import time

# Our modules
import data

from beamie.lib.tokens import do_validate_token

# Our config
from config import CONFIG

"""Module holding useful functions"""

def generate_random_string(length=None, alphabet=None):
    """Static function that generates a random password salt

    :param length: How many digits of salt to generate
    :type length: int
    :returns: A randomly generated salt string
    :rtype: str
    """

    if alphabet is None:
        alphabet = "".join([
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "0123456789",
            "!@#$%^&*()-=_+[]{};:<>/?"
        ])

    if length is None:
        length = random.randint(1, 32)

    return "".join([
        alphabet[
            random.randint(0, len(alphabet) - 1)
        ] for _character in range(length)
    ])

def generate_salt():
    return generate_random_string(random.randint(12,32))

def generate_token(user):
    session = data.session()

    token_id = generate_random_string(40, "".join([
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789"
    ]))
    token_expiry = int(time()) + CONFIG['token_expiry']

    token = data.Token(token_id, token_expiry, user.id)

    log.debug("Token: %s" % token)

    session.add(token)
    session.commit()

    return token.id

def token_in_req_contains_role(req, role):
    """Returns True if the request has a valid X-Auth-Token header that shows
       the user is in the provided role. Returns False if the token's user is
       *not* in the role. Returns None if no token was provided.
    """

    try:
        token_data = do_validate_token(req.headers['x-auth-token'])
    except KeyError:
        return None

    print "Roles: %s" % token_data['user']['roles']
    if roles:
        if role in roles:
            return True

    return False

