# Beamie REST API Documentation - Users

## Concepts

Beamie works in a standard Role-Based Access Control (RBAC) scheme. Your user -
that is; your username and and your salted, one-way hashed password - is
associated with certain roles. These roles dictate what the user is allowed to
do. Here are the roles that matter to the core functionality of Beamie:

 * `disabled` - You cannot authenticate, even with good credentials
 * `listener` - You can perform most actions related to retrieving music from
                the server, and you can save private tags.
 * `contributor` - You can perform actions related to adding data to the server.
 * `administrator` - You can administer the system, make changes to global
                     options, or just about anything else in Beamie.

## Response Bodies

The API calls listed here return the following types of objects in their
responses:

### User

    { "id" : 7,
      "username" : "preferred_username",
      "roles" : [
        "listener",
        "contributor"
    ] }


### POST /users

Creates a new user. Requires an 'administrator' token.

#### Request Body

    { "user" : "preferred_username",
      "password" : "P@ssw0rd#1!",
      "roles" : [
        "listener",
        "contributor"
    ] }


### GET /users/<username>

Retrieves information about a the given user. Requires an 'administrator' token.


### PUT /users/<username>

Updates the given user's password. The provided token must either be
administrative or belonging to the user herself.

#### Request Body

    { "password" : "new_password" }


### DELETE /users/<username>

Deletes the specified user **and all associated data**.

This requires an 'administrator' token, but it is recommended against because
of the effect on other data in the system. Using this function, the deleted data
will be 100% unrecoverable. If you believe that you might not wish to delete all
of this data, it is recommended that you enroll the user in the 'disabled' role.
This effectively prevents the user from accomplishing **anything at all** in
Beamie, while keeping their data intact. Later, removing that 'disabled' role is
sufficient to "restore" the user.


