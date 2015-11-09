# Beamie REST API Documentation - Roles

## Concepts

Roles essentially represent functionality that a user is allowed access to. For
for details on Beamie's default roles, see the Users docs.


## Response Bodies

The API calls listed here return the following types of objects in their
responses:

### Role

    { "id" : 1,
      "name" : "disabled",
      "description" : "Auth always fails for user" }


## API Calls

### POST /roles

Creates a new role.

### Request Body

    { "name" : "role_name",
      "description" : "Clear text explaining the role" }


### GET /roles/<role_name>

Gets information about a role.


### GET /roles/<role_name>/members

Returns a list of usernames enrolled in the given role. Requires an admin token.


### PUT /roles/<role_name>

Updates details of the given role. Requires an administrative token.

### Request Body

The request body must contain at least one of the following fields, or both.

    { "name" : "role_name",
      "description" : "Clear text explaining the role" }


### DELETE /roles/<role_name>

Deletes a role and, naturally, removes all users' memberships.

