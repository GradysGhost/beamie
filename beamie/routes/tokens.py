#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log

# Local imports
from beamie import app, shared
from beamie.lib.auth import Authenticated
from beamie.lib.tokens import do_purge_tokens, do_tidy_tokens, do_revoke_token, do_validate_token

##### ROUTES #####

# POST /tokens
@app.route('/tokens', methods=[ 'POST' ])
def post_tokens():
    return create_token()

# POST /tokens/purge
# Call this to invalidate by deletion all tokens
@app.route('/tokens/purge', methods=[ 'POST' ])
def post_tokens_purge():
    return purge_tokens()

# POST /tokens/tidy
# Call this to delete all expired tokens
@app.route('/tokens/tidy', methods=[ 'POST' ])
def post_tokens_tidy():
    return tidy_tokens()

# GET /tokens/<token_to_validate>
@app.route('/tokens/<token_to_validate>', methods=[ 'GET' ])
def get_tokens(token_to_validate):
    return validate_token(token_to_validate)

# DELETE /tokens/<token_to_revoke>
# Use this to invalidate a token before its expiry
@app.route('/tokens/<token_to_revoke>', methods=[ 'DELETE' ])
def delete_tokens(token_to_revoke):
    return revoke_token(token_to_revoke)


##### HANDLERS #####

# This is Beamie's authentication call. It cannot require prior auth.
def create_token():
    req = flask.request
    data = {}

    ### Input Validation

    # Did the user upload valid JSON?
    try:
        data = json.loads(req.data)
    except ValueError:
        flask.abort(400)

    # Did the user give us good credentials?
    try:
        auth = shared.authenticate(data['user'], data['password'])
    except KeyError:
        flask.abort(400)

    # Cases for invalid user, invalid password, and success
    if auth is None:
        log.debug("Invalid user %s" % data['user'])
        flask.abort(401)
    elif auth is False:
        log.debug("Authentication failed for user %s" % data['user'])
        flask.abort(401)
    else:
        log.debug("Generated token for user %s: %s" % (data['user'], auth))
        resp = flask.make_response(json.dumps({ "token" : auth }))
        resp.headers['Content-Type'] = 'application/json'
        return resp

@Authenticated(['administrator'])
def purge_tokens():
    deleted_count = do_purge_tokens()

    resp = flask.make_response(json.dumps({ 'count' : deleted_count }))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@Authenticated(['administrator'])
def tidy_tokens():
    deleted_count = do_tidy_tokens()

    resp = flask.make_response(json.dumps({ 'count' : deleted_count }))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@Authenticated(['administrator'])
def revoke_token(token_id):
    if do_revoke_token(token_id):
        return ''
    else:
        flask.abort(404)
        

@Authenticated(['administrator'])
def validate_token(token_id):
    token_data = do_validate_token(token_id)
    if token_data:
        resp = flask.make_response(json.dumps(token_data))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        flask.abort(404)

