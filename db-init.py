#!/usr/bin/env python
# -- coding: utf-8 -*-

import argparse

from beamie import data

def create_parser():
    parser = argparse.ArgumentParser(description="Initialize a default Beamie database")

    parser.add_argument(
        "dbstring",
        type=str,
        help="Database connection string, for example: sqlite:///data/new.db"
    )

    return parser

def main():
    # Read input
    opts = create_parser().parse_args()

    # Construct the basic DB framework
    data.construct(opts.dbstring)

    # Get a session
    sesh = data.session(opts.dbstring)
    
    # Create default roles
    roles = [
        data.Role(name="disabled", description="Auth always fails for user"),
        data.Role(name="listener",
            description="Can listen to music and manipulate user-specific settings only`"
        ),
        data.Role(name="contributor", description="Can add music to the library"),
        data.Role(name="administrator", description="Can administer the system")
    ]
    sesh.add_all(roles)

    # Create default user
    root_user = data.User(
        pwhash="35a444966b5be265dee3aad408b3bf92569f097721c253e58229fb69e487df5d1b6b910aa15527071dd2e3c8ae8956f5483ae5627dd0e3f7d3a68cd4a511cbc2",
        salt="/j40+PanDFDLH#xOX4cF4;Hm",
        username="root"
    )
    sesh.add(root_user)

    # Create default role memberships
    memberships = [
        data.RoleMembership(user_id=1, role_id=2),
        data.RoleMembership(user_id=1, role_id=3),
        data.RoleMembership(user_id=1, role_id=4)
    ]
    sesh.add_all(memberships)

    sesh.commit()


if __name__ == "__main__": main()
