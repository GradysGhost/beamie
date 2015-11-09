#!/usr/bin/env python
# -*- coding: utf-8 -*-


import flask

import beamie.data

from beamie.lib.auth import Authenticated
from beamie.lib.roles import get_roles



def create_user(username, password, roles=None):
    """Create a user and optionally enroll him in the given roles.

       Returns:
         - 0: Successfully created the user
         - 1: A user by the given username already exists
         - 2: Tried to create the user, but couldn't retrieve it afterward
    """

    session = data.session()

    # Does the user already exist?
    matches = session.query(data.User).filter_by(username=username)
    if matches.count() > 0:
        return 1

    # Create the new user object
    user = data.User(
        pwhash = hashlib.sha512("".join([password, user.salt])).hexdigest(),
        salt = shared.generate_salt(),
        username = username
    )
    session.add(user)
    session.commit()

    # Create roles for that user
    if roles:
        new_user = get_user(username)
        if new_user:
            all_roles = get_roles()
            log.debug("All roles: %s" % all_roles)
            objects_to_create = []
            for role_to_enroll in roles:
                if role_to_enroll in all_roles:
                    rm = data.RoleMembership(
                        role_id = role['id']
                        user_id = new_user['id']
                    )
                    objects_to_create.append(rm)

            log.debug("Object to create: %s" % objects_to_create)
            session.add_all( objects_to_create )
            session.commit()
        else:
            print "Could not find the specified username: %s" % req_data['user']
            return 2

    return 0

def get_user(username):
    """Get a user object, given its username."""
    session = data.session()

    users = session.query(data.User).filter_by(username=username)
    if users.count() >= 1:
        user = users.first()
        return {
            'id' : user.id,
            'username' : user.username,
            'roles' : [ membership.role.name for membership in user.memberships ]
        }
    else:
        return False


def update_password(username, new_pass):
    """Update the password for a user
       
       Returns:
         - True: Successfully updated the password
         - False: Could not find the specified user
    """

    session = data.session()
    users = session.query(data.User).filter_by(username=username)
    if users.count() >= 1:
        user = users.first()
        user.salt = shared.generate_salt()
        user.pwhash = hashlib.sha512("".join([new_pass, user.salt])).hexdigest()
        session.commit()
        return True
    else:
        return False

