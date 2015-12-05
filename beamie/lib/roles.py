#!/usr/bin/env python
# -*- coding: utf-8 -*-


import beamie.data as data

from beamie.lib.auth import Authorized


def create_role(session, name, description):
    """Creates a new role.
    
       Returns:
         - True: The role was created
         - False: A role already exists by this name
    """

    try:
        session.add(data.Role(description, name))
        session.commit()
        return True
    except IntegrityError:
        return False

def get_role(session, role_name):
    """Gets a role by name.
       
       Returns:
         - dict (Role object): Success
         - None: Role not found
    """

    role = session.query(data.Role).filter_by(name=role_name).first()
    if role is None:
        return None
    return data.todict(role)

def get_roles(session):
    """Gets all roles in the system."""

    roles = [ data.todict(role) for role in session.query(data.Role) ]
    return roles

def get_role_members(session, role_name):
    """Gets a list of all members of the given role.

       Returns:
         - False: Couldn't find the role
         - None: No members of the role
         - list (users): Success
    """
    
    role = get_role(session, role_name)
    if role is None: return False
    if len(role.memberships) == 0: return None
    return [ membership.user.username for membership in role.memberships ]

def update_role(session, role_name, name, description):
    """Updates a role.

       Returns:
         - False: Couldn't find the role
         - True: Updated the role
    """

    role = get_role(session, role_name)
    if role is None: return False

    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    session.commit()
    return True

def delete_role(session, role_name):
    """Deletes a role.

       Returns:
         - False: Couldn't find the role
         - True: Deleted the role
    """

    role = get_role(session, role_name)
    if role is None: return False

    session.delete(role)
    session.commit()
    return True
