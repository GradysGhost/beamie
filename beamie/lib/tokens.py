#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging as log
from time import time

from beamie import data
from beamie.config import CONFIG
from beamie.lib.text import generate_random_string

def tidy_tokens():
    session = data.session()

    expired_tokens = session.query(data.Token).filter(
        data.Token.expiry < int(time()))

    count = expired_tokens.count()
    expired_tokens.delete()

    session.commit()

    return count


def purge_tokens():
    session = data.session()

    to_delete = session.query(data.Token)
    count = to_delete.count()
    to_delete.delete()

    session.commit()
    return count

def generate_token(user):
    session = data.session()
 
    token_id = generate_random_string(40, "".join([
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789"
    ])) 
    token_expiry = int(time()) + CONFIG['token_expiry']
 
    token = data.Token(id = token_id,
                       expiry = token_expiry,
                       user_id = user.id)
 
 
    session.add(token)
    session.commit()

    log.debug("Generated token: %s" % token)
 
    return token.id

def revoke_token(token_id):
    session = data.session()

    tokens = session.query(data.Token).filter_by(id=token_id)
    if tokens.count() >= 1:
        token = tokens.first()
        log.debug("Found token: %s" % token)
        session.delete(token)
        session.commit()
        return True
    else:
        log.debug("Cannot revoke token because it doesn't exist: %s" % token_id)
        return False

def validate_token(token_id):
    ''' Performs token validation. Returns different values under different
        circumstances:
        
          CAUSE                      RETURNS
        - The token is valid       - A JSON object describing the token
        - The token is expired     - False
        - The token doesn't exist  - None
    '''
    token_data = dict()
    session = data.session()

    tokens = session.query(data.Token).filter_by(id=token_id)
    if tokens.count() >= 1:
        token = tokens.first()

        log.debug("Token: %s" % token)
        log.debug("Current time: %i" % time())

        if token.expiry > int(time()):
            token_data['id'] = token.id
            token_data['expiry'] = token.expiry
            token_data['user']  = {
                'username' : token.user.username
            }

            memberships = session.query(data.RoleMembership).filter_by(
                user_id=token.user.id)
            token_data['user']['roles'] = [
                role.role.name for role in memberships
            ]

            log.debug("Token validated: %s" % token_id)
            return token_data
        else:
            log.debug("Token is expired; deleting: %s" % token_id)
            revoke_token(token_id)
            return False

    else:
        log.debug("Could not find token %s; it is invalid" % token_id)
        return None

