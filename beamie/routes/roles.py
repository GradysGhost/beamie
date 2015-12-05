#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log

# Local imports
from beamie import app, data
from beamie.lib.auth import Authorized, authenticate
from beamie.lib.roles import create_role, get_role, get_roles

DEFAULT_HEADERS = { "Content-Type" : "application/json" }

##### ROUTES #####

# POST /roles
@app.route('/roles', methods=[ 'POST' ])
@data.Session()
def post_roles(*args, **kwargs):
    """Route POSTs to /roles."""

    handle_post_roles(kwargs['session'])

# GET /roles
@app.route('/roles', methods=[ 'GET' ])
@data.Session()
def get_roles():
    """Route GETs to /roles."""

    return handle_get_roles(kwargs['session'])

# GET /roles/<role_name>
@app.route('/roles/<role_name>', methods=[ 'GET' ])
@data.Session()
def get_roles_role(role_name):
    """Route GETs to /roles/<role_name>."""

    return handle_get_roles_role_name(kwargs['session'], role_name)

# GET /roles/<role_name>/members
@app.route('/roles/<role_name>/members', methods=[ 'GET' ])
@data.Session()
def get_roles_role_members(role_name):
    """Route GETs to /roles/<role_name>/members."""

    return handle_get_roles_role_name_members(kwargs['session'], role_name)

# PUT /roles/<role_name>
@app.route('/roles/<role_name>', methods=[ 'PUT' ])
@data.Session()
def put_roles_role_members(role_name):
    """Route PUTs to /roles/<role_name>."""

    return handle_put_roles_role_name(kwargs['session'], role_name)

# DELETE /roles/<role_name>
@app.route('/roles/<role_name>', methods=[ 'DELETE' ])
@data.Session()
def delete_roles_token(role_name):
    """Route DELETEs to /roles/<role_name>."""

    return handle_delete_roles_role_name(kwargs['session'], role_name)


##### HANDLERS #####

@Authorized(['administrator'])
def handle_post_roles(session):
    """Handles logic and data transformation for POSTs to /roles."""

    req = flask.request
    req_data = dict()

    try:
        req_data = json.loads(req.data)
        if create_role(session, req_data['name'], req_data['description']):
            return flask.make_response(
              json.dumps(get_role(session, req_data['name'])),
              200,
              DEFAULT_HEADERS
            )
        else:
    except KeyError:
        return flask.make_response(
          json.dumps({
            'error' : 'Missing "name" or "description"'
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

@Authorized(['listener', 'contributor', 'administrator'])
def handle_get_roles(session):
    """Handles logic and data transformation for GETs to /roles."""

    return flask.make_response(
        json.dumps(get_roles(session)),
        200,
        DEFAULT_HEADERS
    )

@Authorized(['listener', 'contributor', 'administrator'])
def handle_get_roles_role_name(session, role_name):
    """Handles logic and data transformation for GETs to /roles/<role_name>."""

    role = get_role(role_name)

    if role is None:
        return flask.make_response('', 404, DEFAULT_HEADERS)

    return flask.make_response(
        json.dumps(data.todict(role)),
        200,
        DEFAULT_HEADERS
    )

@Authorized(['listener', 'contributor', 'administrator'])
def handle_get_roles_role_name_members(session, role_name):
    """Handles logic and data transformation for GETs to /roles/<role_name>/members."""

    members = get_role_members(session, role_name)
    if members is False:
        return flask.make_response('', 404, DEFAULT_HEADERS)
    if members is None:
        return flask.make_response('[]', 200, DEFAULT_HEADERS)

    return flask.make_response(
        json.dumps(members),
        200,
        DEFAULT_HEADERS
    )

@Authorized(['administrator'])
def handle_put_roles_role_name(session, role_name):
    """Handles logic and data transformation for PUTs to /roles/<role_name>."""

    req = flask.request
    req_data = dict()

    try:
        req_data = json.loads(req.data)
        if 'name' not in req_data and 'description' not in req_data:
            raise KeyError

        if 'name' not in req_data:
            req_data['name'] = None
        if 'description' not in req_data:
            req_data['description'] = None

        if update_role(session, role_name, req_data['name'], req_data['description']):
            return flask.make_response('', 200, DEFAULT_HEADERS)
        else:
            return flask.make_response('', 404, DEFAULT_HEADERS)
    except KeyError:
        return flask.make_response(
            json.dumps(
                { 'error' : 'Missing "name" or "description"' }
            ),
            400,
            DEFAULT_HEADERS
        )

@Authorized(['administrator'])
def handle_delete_roles_role_name(session, role_name):
    """Handles logic and data transformation for DELETEs to /roles/<role_name>."""

        if delete_role(role_name):
            return flask.make_response('', 200, DEFAULT_HEADERS)
        return flask.make_response('', 404, DEFAULT_HEADERS)

