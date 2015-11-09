#!/usr/bin/env python
# -*- coding: utf-8 -*-


import beamie.data

from beamie.lib.auth import Authorized




@Authorized(["listener", "contributor", "administrator"])
def get_roles():
    session = data.session()
    roles = [ {
        'id' : role.id,
        'name' : role.name,
        'description' : role.description
    } for role in session.query(data.Role) ]
    return roles

