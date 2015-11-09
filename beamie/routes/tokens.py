#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log

# Local imports
from beamie import app
from beamie.lib.auth import Authorized, authenticate
from beamie.lib.tokens import \
    purge_tokens, tidy_tokens, revoke_token, validate_token

DEFAULT_HEADERS = { "Content-Type" : "application/json" }

##### ROUTES #####

# POST /tokens
@app.route('/tokens', methods=[ 'POST' ])
def post_tokens():
    """Route POSTs to /tokens."""

    return handle_post_tokens()

# POST /tokens/purge
# Call this to invalidate by deletion all tokens
@app.route('/tokens/purge', methods=[ 'POST' ])
def post_tokens_purge():
    """Route POSTs to /tokens/purge."""

    return handle_post_tokens_purge()

# POST /tokens/tidy
# Call this to delete all expired tokens
@app.route('/tokens/tidy', methods=[ 'POST' ])
def post_tokens_tidy():
    """Route POSTs to /tokens/tidy."""

    return handle_post_tokens_tidy()

# GET /tokens/<token_to_validate>
@app.route('/tokens/<token>', methods=[ 'GET' ])
def get_tokens_token(token):
    """Route GETs to /tokens/<token>."""

    return handle_get_tokens_token(token)

# DELETE /tokens/<token_to_revoke>
# Use this to invalidate a token before its expiry
@app.route('/tokens/<token>', methods=[ 'DELETE' ])
def delete_tokens_token(token):
    """Route DELETEs to /tokens/<token>."""

    return handle_delete_tokens_token(token)


##### HANDLERS #####

# This is Beamie's authentication call. It cannot require prior auth.
def handle_post_tokens():
    """Handles logic and data transformation for POSTs to /tokens."""

    req = flask.request
    data = {}

    ### Input Validation

    # Did the user upload valid JSON?
    try:
        data = json.loads(req.data)
    except ValueError:
        return flask.make_response(
            json.dumps({
                'error' : 'Invalid JSON'
            }),
            400,
            DEFAULT_HEADERS
        )

    # Did the user give us good credentials?
    try:
        auth = authenticate(data['username'], data['password'])
    except KeyError:
        return flask.make_response(
            json.dumps({
                'error' : 'Missing username or password data'
            }),
            400,
            DEFAULT_HEADERS
        )

    # Cases for invalid user, invalid password, and success
    if auth is None:
        log.debug("Invalid user %s" % data['username'])
        return flask.make_response('', 401)
    elif auth is False:
        log.debug("Authentication failed for user %s" % data['username'])
        return flask.make_response('', 401)
    else:
        log.debug("Generated token for user %s: %s" % (data['username'], auth))
        return flask.make_response(
            json.dumps({
                'token' : auth
            }),
            200,
            DEFAULT_HEADERS
        )

@Authorized(['administrator'])
def handle_post_tokens_purge():
    """Handles logic and data transformation for POSTs to /tokens/purge."""

    deleted_count = purge_tokens()

    return flask.make_response(
        json.dumps({
            'count' : deleted_count
        }),
        200,
        DEFAULT_HEADERS
    )

@Authorized(['administrator'])
def handle_post_tokens_tidy():
    """Handles logic and data transformation for POSTs to /tokens/tidy."""

    deleted_count = tidy_tokens()

    return flask.make_response(
        json.dumps({
            'count' : deleted_count
        }),
        200,
        DEFAULT_HEADERS
    )

@Authorized(['administrator'])
def handle_delete_tokens_token(token_id):
    """Handles logic and data transformation for DELETEs to /tokens/<token>."""

    if revoke_token(token_id):
        return flask.make_response('', 200)
    else:
        return flask.make_response('', 404)
        
@Authorized(['administrator'])
def handle_get_tokens_token(token_id):
    """Handles logic and data transformation for GETs to /tokens/<token>."""

    token_data = validate_token(token_id)
    if token_data:
        return flask.make_response(
            json.dumps(token_data),
            200,
            DEFAULT_HEADERS
        )
    else:
        flask.make_response('', 404)

