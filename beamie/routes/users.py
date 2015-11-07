#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log

# Local imports
from beamie import app, shared
from beamie.lib.auth import Authenticated
from beamie.lib.tokens import do_validate_token

##### ROUTES #####

# POST /users
# Create a new user
@app.route('/users', methods=[ 'POST' ])
def create_user():
    return create_user()

# PUT /users/<username>
# Update a user's password
@app.route('/users/<username>', methods=[ 'PUT' ])
def update_password(username):
    return update_password(username)



##### HANDLERS #####

def get_user(username):
    session = data.session()

    users = session.query(data.User).filter_by(username=username)
    if users.count() >= 1:
        user = users.first()
        return {
            'id' : user.id,
            'name' : user.username
        }
    else:
        return False

@Authenticated(["listener", "contributor", "administrator"])
def get_roles():
    session = data.session()
    roles = [ {
        'id' : role.id,
        'name' : role.name,
        'description' : role.description
    } for role in session.query(data.Role) ]
    return roles

@Authenticated(['administrator'])
def create_user():
    req = flask.request
    # req_data = {}   # Marked for deletion

    try:
        req_data = json.loads(req.data)
        if 'user' not in req_data or 'password' not in req_data:
            flask.abort(400)
    except ValueError:
        flask.abort(400)

    session = data.session()

    user = data.User()
    user.username = req_data['user']
    user.salt = shared.generate_salt()
    user.pwhash = hashlib.sha512("".join([req_data['password'], user.salt])).hexdigest()

    session.add(user)
    session.commit()

    new_user = get_user(req_data['user'])
    if new_user:
        all_roles = get_roles()
        log.debug("All roles: %s" % all_roles)
        objects_to_create = []
        for role_to_enroll in req_data['roles']:
            for role in all_roles:
                if role['name'] == role_to_enroll:
                    rm = data.RoleMembership()
                    rm.user_id = new_user['id']
                    rm.role_id = role['id']
                    objects_to_create.append(rm)

        log.debug("Object to create: %s" % objects_to_create)
        session.add_all( objects_to_create )
        session.commit()
        return ''
    else:
        print "Could not find the specified username: %s" % req_data['user']
        flask.abort(500)

@Authenticated(['administrator'])
def create_user():
    req = flask.request
    req_data = {}

    try:
        req_data = json.loads(req.data)
        if 'user' not in req_data or 'password' not in req_data:
            flask.abort(400)
    except ValueError:
        flask.abort(400)

    session = data.session()

    user = data.User()
    user.username = req_data['user']
    user.salt = shared.generate_salt()
    user.pwhash = hashlib.sha512("".join([req_data['password'], user.salt])).hexdigest()

    session.add(user)
    session.commit()

    new_user = get_user(req_data['user'])
    if new_user:
        all_roles = get_roles()
        log.debug("All roles: %s" % all_roles)
        objects_to_create = []
        for role_to_enroll in req_data['roles']:
            for role in all_roles:
                if role['name'] == role_to_enroll:
                    rm = data.RoleMembership()
                    rm.user_id = new_user['id']
                    rm.role_id = role['id']
                    objects_to_create.append(rm)

        log.debug("Object to create: %s" % objects_to_create)
        session.add_all( objects_to_create )
        session.commit()
        return ''
    else:
        print "Could not find the specified username: %s" % req_data['user']
        flask.abort(500)

def update_password(username):
    # Because we need to verify that either the user making the request is
    # an administrator or that the request is being made to change the password
    # of the user making the request, this function cannot use the
    # @Authenticated decorator, and we must do a special kind of auth here.
    req = flask.request
    req_data = {}

    try:
        req_data = json.loads(req.data)
        print("Request data: %s" % req_data)
    except ValueError:
        flask.abort(400)

    authorized = False
    try:
        token_data = do_validate_token(req.headers['x-auth-token'])
    except KeyError:
        token_data = None
        
    if token_data is not None:
        if token_data['user']['username'] == username:
            authorized = True
        else:
            if shared.token_in_req_contains_role(req, 'administrator'):
                authorized = True

    # Next line is for debugging ONLY
    # authorized = True

    if authorized:
        session = data.session()
        users = session.query(data.User).filter_by(username=username)
        if users.count() >= 1:
            user = users.first()
            user.salt = shared.generate_salt()
            user.pwhash = hashlib.sha512("".join([req_data['password'], user.salt])).hexdigest()
            session.commit()
            return ''
        else:
            flask.abort(400)
    else:
        flask.abort(401)

