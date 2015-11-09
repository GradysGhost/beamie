# Beamie REST API Documentation - Tokens

## Concepts

Beamie uses a token-based authentication scheme. First, `POST` to `/tokens` with
your username and password to log in and create a token. Thereafter, pass this
token's ID along with every request in the form of an `X-Auth-Token` header.

The default username and password is 'root' / 'adminpass'.

## Response Bodies

The API calls listed here return the following types of objects in their
responses:

### Token

    {
        "id": "abcdefgh01292t3jsjz899oij3",
        "exp": 1442846339,
        "user": {
            "id": 1,
            "username": "root",
            "roles": [
                "listener",
                "contributor",
                "administrator"
            ]
        }
    }


### POST /tokens

Authenticates a user and responds with a token.

#### Request Body

    { "username" : "<username>",
      "password" : "<password>" }


### GET /tokens/<token_id>

Responds with information about the token and the user it belongs to, provided
it's a valid token.

Note that the token passed in the request path is the token you are trying to
validate. You must already be authenticated to make this request, and will have
to pass a valid token in the `X-Auth-Token` header lest you receive a 401 in
response.


### DELETE /tokens/<token_id>

Instantly revokes the specified token. You must be the owner of the token or
an 'administrator' to perform this action.


### POST /tokens/tidy

Instantly revokes any and all expired tokens. These tokens will ordinarily be
revoked the moment a client tries to use one, but this can help keep the
database clean. You must provide an 'adminstrator' token to perform this action.

#### Response Body

    { "count" : num_of_tokens_revoked }


### POST /tokens/purge

Instantly revokes all tokens. All of them. Every one. You need an
'administrator' token to do this.

#### Response Body

    { "count" : num_of_tokens_revoked }

