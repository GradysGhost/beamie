#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A basic CRUD data layer for Beamie using SQLAlchemy
"""

# Imports
import hashlib
import logging as log
import random

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.schema import PrimaryKeyConstraint

from config import CONFIG
from beamie.lib.text import generate_salt

# Create a base mapping to extend into our data classes
BaseMapping = declarative_base()


def engine(db_string=CONFIG['db_string']):
    return create_engine(db_string)

def session(db_string=CONFIG['db_string']):
    """Creates a DB session"""
    eng = engine(db_string)
    session = sessionmaker(bind=eng)()
    return session

def construct(db_string=CONFIG['db_string']):
    eng = engine(db_string)
    BaseMapping.metadata.drop_all(eng)
    BaseMapping.metadata.create_all(eng)
    session = sessionmaker(bind=eng)()
    
    role_disabled = Role('disabled', 'User cannot auth')
    role_disabled.id = 1
    role_listener = Role('listener', 'User can listen')
    role_listener.id = 2
    role_contributor = Role('contributor', 'User can upload')
    role_contributor.id = 3
    role_administrator = Role('administrator', 'User can administer Beamie')
    role_administrator.id = 4
    session.add_all([role_disabled, role_listener, role_contributor, role_administrator])

    salt = generate_salt()
    root_user = User(
        hashlib.sha512("".join(['adminpass', salt])).hexdigest(),
        salt,
        'root'
    )
    root_user.id = 1
    session.add(root_user)
    session.commit()

    memberships = [
        RoleMembership(2, 1),
        RoleMembership(3, 1),
        RoleMembership(4, 1)
    ]
    session.add_all(memberships)
    session.commit()

def todict(db_obj):
    obj_dict = dict()
    obj_vars = [ var for var in vars(db_obj) if not var.startswith('_') ]
    for var in obj_vars:
        obj_dict[var] = getattr(db_obj, var)
    return obj_dict
      

# Session wrapper
class Session(object):
    """A decorator to wrap functions in database sessions."""

    def __init__(self):
        """Create a new Session wrapper."""

        self.session = session()

    def __call__(self, f):
        """Call the function with a session variable."""

        def wrapped_f(*args, **kwargs):
            kwargs['session'] == self.session
            ret = f(*args, **kwargs)
            self.session.close()
            return ret

        return wrapped_f

# Data classes go here
class Artist(BaseMapping):
    __tablename__ = 'artist'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(250), unique=True)

    albums = relationship("Album",
        backref=backref("artist",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    tags = relationship("ArtistTag",
        backref=backref("artist",
        cascade="all, delete-orphan",
        single_parent=True
    ))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Artist<id=%i, name='%s'>" % (self.id, self.name)

class ArtistTag(BaseMapping):
    __tablename__ = 'artist_tag'

    id = Column('id', Integer, primary_key=True)
    artist_id = Column('artist', Integer, ForeignKey("artist.id"))
    is_global = Column('global', Boolean)
    tag = Column('tag', String(250))
    user_id = Column('user', Integer, ForeignKey("user.id"))

    def __init__(self, artist_id, is_global, tag, user_id):
        self.artist_id, self.is_global, self.tag, self.user_id = \
            artist_id, is_global, tag, user_id

    def __repr__(self):
        return "ArtistTag<id=%i, artist_id=%i, is_global=%s, tag='%s', user_id=%i>" % (
            self.id, self.artist_id, self.is_global, self.tag, self.user_id)

class Album(BaseMapping):
    __tablename__ = 'album'

    id = Column('id', Integer, primary_key=True)
    artist_id = Column('artist', Integer, ForeignKey("artist.id"))
    name = Column('name', String(250))

    tags = relationship("AlbumTag",
        backref=backref("album",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    tracks = relationship("Track",
        backref=backref("album",
        cascade="all, delete-orphan",
        single_parent=True
    ))

    def __init__(self, artist_id, name):
        self.artist_id, self.name = artist_id, name

    def __repr__(self):
        return "Album<id=%i, artist_id=%i, name='%s'>" % (
            self.id, self.artist_id, self.name)

class AlbumTag(BaseMapping):
    __tablename__ = 'album_tag'

    id = Column('id', Integer, primary_key=True)
    album_id = Column('album', Integer, ForeignKey("album.id"))
    is_global = Column('global', Boolean)
    tag = Column('tag', String(250))
    user_id = Column('user', Integer, ForeignKey("user.id"))

    def __init__(self, album_id, is_global, tag, user_id):
        self.album_id, self.is_global, self.tag, self.user_id = \
            album_id, is_global, tag, user_id

    def __repr__(self):
        return "AlbumTag<id=%i, album_id=%i, is_global=%s, tag='%s', user_id=%i>" % (
            self.id, self.album_id, self.is_global, self.tag, self.user_id)

class Option(BaseMapping):
    __tablename__ = 'option'

    key = Column('key', String(250), primary_key=True)
    user_id = Column('user', Integer, ForeignKey("user.id"), primary_key=True)
    value = Column('value', String(250))

    def __init__(self, key, user_id, value):
        self.key, self.user_id, self.value = key, user_id, value

    def __repr__(self):
        return "Option<key='%s', user_id=%i, value='%s'>" % (
            self.key, self.user_id, self.value)

class Player(BaseMapping):
    __tablename__ = 'player'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(250))
    queue_position = Column('queue_position', Integer)
    track_position = Column('track_position', Integer)
    user_id = Column('user', Integer, ForeignKey("user.id"))

    tracks = relationship("PlayerTrack",
        backref=backref("player",
            cascade="all, delete-orphan",
            single_parent=True
    ))

    def __init__(self, name, queue_position, track_position, user_id):
        self.name, self.queue_position, self.track_position, self.user_id = \
            name, queue_position, track_position, user_id

    def __repr__(self):
        return "Player<id=%i, name='%s', queue_position=%i, track_position=%i, user_id=%i>" % (
            self.id, self.name, self.queue_position, self.track_position, self.user_id)

class PlayerTrack(BaseMapping):
    __tablename__ = 'player_track'

    id = Column('id', Integer, primary_key=True)
    player_id = Column('player', Integer, ForeignKey("player.id"))
    sequence = Column('sequence', Integer)
    track_id = Column('track', Integer, ForeignKey("track.id"))

    def __init__(self, player_id, sequence, track_id):
        self.player_id, self.sequence, self.track_id = player_id, sequence, track_id
    
    def __repr__(self):
        return "PlayerTrack<id=%i, player_id=%i, sequence=%i, track_id=%i>" % (
            self.id, self.player_id, self.sequence, self.track_id)

class Playlist(BaseMapping):
    __tablename__ = 'playlist'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(250))
    user_id = Column('user', Integer, ForeignKey("user.id"))

    tracks = relationship("PlaylistTrack",
        backref=backref("playlist",
            cascade="all, delete-orphan",
            single_parent=True
    ))

    def __init__(self, name, user_id):
        self.name, self.user_id = name, user_id

    def __repr__(self):
        return "Playlist<id=%i, name=%s, user_id=%i>" % (
            self.id, self.name, self.user_id)

class PlaylistTrack(BaseMapping):
    __tablename__ = 'playlist_track'

    id = Column('id', Integer, primary_key=True)
    playlist_id = Column('playlist', Integer, ForeignKey("playlist.id"))
    sequence = Column('sequence', Integer)
    track_id = Column('track', Integer, ForeignKey("track.id"))

    track = relationship("Track", uselist=False)

    def __init__(self, playlist_id, sequence, track_id):
        self.playlist_id, self.sequence, self.track_id = \
            playlist_id, sequence, track_id

    def __repr__(self):
        return "PlaylistTrack<id=%i, playlist_id=%i, sequence=%i, track_id=%i>" % (
            self.id, self.playlist_id, self.sequence, self.track_id)

class Query(BaseMapping):
    __tablename__ = 'query'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(250))
    user_id = Column('user', Integer, ForeignKey("user.id"))

    filters = relationship("QueryFilter",
        backref=backref("query",
            cascade="all, delete-orphan",
            single_parent=True
    ))

    def __init__(self, name, user_id):
        self.name, self.user_id = name, user_id

    def __repr__(self):
        return "Query<id=%i, name='%s', user_id=%i>" % (
            self.id, self.name, self.user_id)

class QueryFilter(BaseMapping):
    __tablename__ = 'query_filter'

    id = Column('id', Integer, primary_key=True)
    is_and = Column('and', Boolean, default=True)
    comparison = Column('comparison', String(250))
    key = Column('key', String(250))
    query_id = Column('query', Integer, ForeignKey("query.id"))
    sequence = Column('sequence', Integer)
    value = Column('value', String(250))
    value_int = Column('value_int', Boolean, default=False)

    def __init__(self,
                 is_and,
                 comparison,
                 key,
                 query_id,
                 sequence,
                 value,
                 value_int):
        self.is_and, self.comparison, self.key, self.query_id, \
            self.sequence, self.value, self.value_int = \
                is_and, comparison, key, query_id, sequence, value, value_int

    def __repr__(self):
        return "QueryFilter<id=%i, is_and=%s, comparison='%s', key='%s', " \
               "query_id=%i, sequence=%i, value='%s', value_int=%s>" % (
                    self.id, self.is_and, self.comparison, self.key,
                    self.query_id, self.sequence, self.value, self.value_int)

class Role(BaseMapping):
    __tablename__ = 'role'

    id = Column('id', Integer, primary_key=True)
    description = Column('description', String(250))
    name = Column('name', String(250), unique=True)

    memberships = relationship("RoleMembership",
        backref=backref("role",
            cascade="all, delete-orphan",
            single_parent=True
    ))

    def __init__(self, name, description):
        self.description, self.name = description, name

    def __repr__(self):
        return "Role<id=%i, description='%s', name='%s'>" % (
            self.id, self.description, self.name)

class RoleMembership(BaseMapping):
    __tablename__ = 'role_membership'

    role_id = Column('role', Integer, ForeignKey("role.id"), primary_key=True)
    user_id = Column('user', Integer, ForeignKey("user.id"), primary_key=True)

    def __init__(self, role_id, user_id):
        self.role_id, self.user_id = role_id, user_id

    def __repr__(self):
        return "RoleMembership<role_id=%i, user_id=%i>" % (
            self.role_id, self.user_id)

class Token(BaseMapping):
    __tablename__ = 'token'

    id = Column('id', String(250), primary_key=True)
    expiry = Column('expiry', Integer)
    user_id = Column('user', Integer, ForeignKey("user.id")) 

    def __init__(self, id, expiry, user_id):
        self.id, self.expiry, self.user_id = id, expiry, user_id

    def __repr__(self):
        return "Token<id='%s', expiry=%i, user_id=%i>" % (
            self.id, self.expiry, self.user_id)

class Track(BaseMapping):
    __tablename__ = 'track'

    id = Column('id', Integer, primary_key=True)
    album_id = Column('album', Integer, ForeignKey("album.id"))
    filename = Column('filename', String(250), unique=True)
    name = Column('name', String(250))
    number = Column('number', Integer)

    player_items = relationship("PlayerTrack",
        backref=backref("track",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    tags = relationship("TrackTag",
        backref=backref("track",
            cascade="all, delete-orphan",
            single_parent=True
    ))

    def __init__(self, album_id, filename, name, number):
        self.album_id, self.filename, self.name, self.number = \
            album_id, filename, name, number

    def __repr__(self):
        return "Track<id=%i, album_id=%i, filename='%s', name='%s', number=%i>" % (
            self.id, self.album_id, self.filename, self.name, self.number)

class TrackTag(BaseMapping):
    __tablename__ = 'track_tag'

    id = Column('id', Integer, primary_key=True)
    is_global = Column('global', Boolean)
    tag = Column('tag', String(250))
    track_id = Column('track', Integer, ForeignKey("track.id"))
    user_id = Column('user', Integer, ForeignKey("user.id"))

    def __init__(self, is_global, tag, track_id, user_id):
        self.is_global, self.tag, self.track_id, self.user_id = \
            is_global, tag, track_id, user_id

    def __repr__(self):
        return "TrackTag<id=%i, is_global=%s, tag='%s', track_id=%i, user_id=%i>" % (
            self.id, self.is_global, self.tag, self.track_id, self.user_id)

class User(BaseMapping):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True)
    pwhash = Column('pwhash', String(250))
    salt = Column('salt', String(250))
    username = Column('username', String(250), unique=True)

    album_tags = relationship("AlbumTag",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    artist_tags = relationship("ArtistTag",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    memberships = relationship("RoleMembership",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    options = relationship("Option",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    players = relationship("Player",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    queries = relationship("Query",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    tokens = relationship("Token",
        backref=backref("user",
            cascade="all, delete-orphan",
            single_parent=True
    ))
    track_tags = relationship("TrackTag",
        backref=backref("user",
        cascade="all, delete-orphan",
        single_parent=True
    ))

    def __init__(self, pwhash, salt, username):
        self.pwhash, self.salt, self.username = pwhash, salt, username

    def __repr__(self):
        return "User<id=%i, pwhash='%s', salt='%s', username='%s'>" % (
            self.id, self.pwhash, self.salt, self.username)

