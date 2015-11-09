#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log

# Local imports
from beamie import app
from beamie.lib.auth import Authorized
from beamie.lib.tokens import validate_token
from beamie.lib.users import create_user, get_user, update_password, delete_user

DEFAULT_HEADERS = { "Content-Type" : "application/json" }

##### ROUTES #####

# POST /users
# Create a new user
@app.route('/users', methods=[ 'POST' ])
def post_users():
    """Route POSTs to /users"""

    return handle_post_users()

# PUT /users/<username>
# Update a user's password
@app.route('/users/<username>', methods=[ 'PUT' ])
def put_users_username(username):
    """Route PUTs to /users/<username>"""

    return handle_put_users_username(username)

# GET /users/<username>
# Get a user object
@app.route('/users/<username>', methods=['GET'])
def get_users_username(username):
    """Route GETs to /users/<username>"""

    return handle_get_users_username(username)

# DELETE /users/<username>
# Delete a user object and all associated data
@app.route('/users/<username>', methods=['DELETE'])
def delete_users_username(username):
    """Route DELETEs to /users/<username>"""

    return handle_delete_users_username(username)


##### HANDLERS #####

@Authorized(['administrator'])
def handle_post_users():
    """Handles logic and data transformation for POSTs to /users"""

    req = flask.request

    try:
        req_data = json.loads(req.data)
        if 'username' not in req_data or 'password' not in req_data:
            return flask.make_response(
                json.dumps({
                    'error' : 'Missing username or password data'
                }),
                400,
                DEFAULT_HEADERS
            )
    except ValueError:
        return flask.make_response(
            json.dumps({
                'error' : 'Invalid JSON'
            }),
            400,
            DEFAULT_HEADERS
        )

    if 'roles' in req_data:
        ret_code = create_user(req_data['username'],
                               req_data['password'],
                               req_data['roles'])
    else:
        ret_code = create_user(req_data['username'],
                               req_data['password'])

    if ret_code is True:
        return flask.make_response(json.dumps(get_user(req_data['username'])), 200)
    elif ret_code is False:
        return flask.make_response(
            json.dumps({
                'error' : 'A user already exists with username "%s"' % (
                    req_data['username'])
            }),
            412,
            DEFAULT_HEADERS
        )
    elif ret_code is None:
        return flask.make_response(
            json.dumps({
                'error' : 'Could not retrieve user data after creating it'
            }),
            500,
            DEFAULT_HEADERS
        )
    else:
        return flask.make_response('', 500)


def handle_put_users_username():
    """Handles logic and data transformation for PUTs to /users/<username>"""

    req = flask.request

    try:
        req_data = json.loads(req.data)
        if 'password' not in req_data:
            return flask.make_response(
                json.dumps({
                    'error' : 'Missing password data'
                }),
                400,
                DEFAULT_HEADERS
            )
    except ValueError:
        return flask.make_response(
            json.dumps({
                'error' : 'Invalid JSON'
            }),
            400,
            DEFAULT_HEADERS
        )

    # Is the user authorized? Must be admin or self.
    authorized = False
    try:
        token_data = do_validate_token(req.headers['x-auth-token'])
    except KeyError:
        token_data = None

    if token_data is not None:
        # Token is for self
        if token_data['user']['username'] == username:
            authorized = True

        # Token is administrative
        elif 'administrator' in token_data['roles']:
            authorized = True

    if authorized:
        if update_password(username, req_data['password']):
            return flask.make_response('', 200)
        else:
            return flask.make_response('', 404)
    else:
        return flask.make_response('', 401)


def handle_get_users_username(username):
    """Handles logic and data transformation for GETs to /users/<username>"""
    user = get_user(username)

    if user:
        return flask.make_response(
            json.dumps(user),
            200,
            DEFAULT_HEADERS
            )
    else:
        return flask.make_response('', 404)


@Authorized(['administrator'])
def handle_delete_users_username(username):
    """Handles logic and data transformation for DELETEs to /users/<username>"""
    if delete_user(username):
        return flask.make_response('', 200)
    else:
        return flask.make_response('', 404)

