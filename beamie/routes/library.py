#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
import flask
import json
import logging as log
import os

# Local imports
from beamie import app, data
from beamie.config import CONFIG
from beamie.lib.auth import Authorized
from beamie.lib.mediascanner import MediaScanner

##### ROUTE DEFINITIONS #####

# POST /scan -- Scan the library for orphaned DB entries and new tracks; repair things
@app.route('/scan', methods=[ 'POST' ])
def scan():
    return scan()

# GET /tracks
@app.route('/tracks', methods=[ 'GET' ])
def tracks():
    req = flask.request

    tracks = [ { "id" : item.id,
                 "album_id" : item.album.id,
                 "album" : item.album.name,
                 "artist_id" : item.album.artist.id,
                 "artist" : item.album.artist.name,
                 "name" : item.name,
                 "number" : item.number,
                 "filename" : item.filename
               } for item in get_tracks(req.args) ]

    log.debug("Tracks: %s; Type: %s" % ( tracks, type(tracks)))

    resp = flask.make_response(json.dumps(tracks))
    resp.headers['Content-Type'] = 'application/json'
    return resp

# GET /tracks/<track_id>
@app.route('/tracks/<int:track_id>', methods=[ 'GET' ])
def get_track(track_id):
    track = get_tracks({ "id" : track_id }).first()
    log.debug("Track: %s" % track)
    resp = flask.make_response(json.dumps({
        "id" : track.id,
        "album_id" : track.album.id,
        "album" : track.album.name,
        "artist_id" : track.album.artist.id,
        "artist" : track.album.artist.name,
        "name" : track.name,
        "number" : track.number,
        "filename" : track.filename
    }))
    resp.headers['Content-Type'] = 'application/json'
    return resp

# GET /tracks/<track_id>/download
@app.route('/tracks/<int:track_id>/download', methods=[ 'GET' ])
def download_track(track_id):
    tracks = get_tracks({ "id" : track_id })

    if tracks.count() == 0:
        log.debug("No tracks with ID %i" % track_id)
        flask.abort(404)
    else:
        filename = tracks.first().filename

        try:
            resp = flask.make_response(open(filename, 'r').read())
            if filename.endswith('.mp3'):
                resp.headers['Content-Type'] = 'audio/mpeg3'
            else:
                resp.headers['Content-Type'] = 'application/octet-stream'
            return resp
        except IOError:
            log.warning("Could not read file %s" % filename)
            flask.abort(500)

# GET /albums
@app.route('/albums', methods=[ 'GET' ])
def albums():
    req = flask.request

    albums = [ { "id" : album.id,
                 "artist" : album.artist.name,
                 "artist_id" : album.artist.id,
                 "name" : album.name
               } for album in get_albums(req.args) ]

    resp = flask.make_response(json.dumps(albums))
    resp.headers['Content-Type'] = 'application/json'
    return resp

# GET /albums/<album_id>
@app.route('/albums/<int:album_id>', methods=[ 'GET' ])
def get_album(album_id):
    albums = [ { "id" : album.id,
                 "artist" : album.artist.name,
                 "artist_id" : album.artist.id,
                 "name" : album.name
               } for album in get_albums({ "id" : album_id }) ]

    if len(albums) == 0:
        log.debug("No albums with ID %i" % track_id)
        flask.abort(404)
    else:
        resp = flask.make_response(json.dumps(albums[0]))
        resp.headers['Content-Type'] = 'application/json'
        return resp

# GET /artists
@app.route('/artists', methods=[ 'GET' ])
def artists():
    req = flask.request

    artists = [ { "id" : artist.id, "name" : artist.name }
        for artist in get_artists(req.args) ]

    resp = flask.make_response(json.dumps(artists))
    resp.headers['Content-Type'] = 'application/json'
    return resp

# GET /artists/<artist_id>
@app.route('/artists/<int:artist_id>', methods=[ 'GET' ])
def get_artist(artist_id):
    artists = get_artists({ "id" : artist_id })

    if artists.count() == 0:
        log.debug("No artists with ID %i" % track_id)
        flask.abort(404)
    else:
        artist = artists.first()
        artist_obj = { "id" : artist.id, "name" : artist.name }
        resp = flask.make_response(json.dumps(artist_obj))
        resp.headers['Content-Type'] = 'application/json'
        return resp



##### HANDLERS #####

@Authorized(['contributor', 'administrator'])
def scan():
    outcome = {
        "orphans" : list(),
        "discoveries" : {
            "artists" : list(),
            "albums" : list(),
            "tracks" : list()
        }
    }

    scanner = MediaScanner(CONFIG['media_paths'])
    scanner.files = scanner.find_files(CONFIG['media_paths'])
    scanner.scan_files()

    # Connect to the database
    session = data.session(CONFIG['sqlite_db'])

    # Are there any entries in the database that don't exist on disk anymore?
    tracks = session.query(data.Track)

    for track in tracks:
        try:
            os.stat(track.filename)
        except OSError, e:
            session.delete(track)
            outcome['orphans'].append({
                "id" : track.id,
                "number" : track.number,
                "name" : track.name,
                "album" : track.album.name,
                "artist" : track.album.artist.name,
                "filename" : track.filename
            })
            log.debug("Found an orphaned reference to %s" % track.filename)

    session.commit()

    # Init
    artists_to_add = list()
    albums_to_add = list()
    tracks_to_add = list()

    # Scan for uncreated artists and create them
    for tag in scanner.tags:
        artist = u''.join(tag.tag['artist'])
        artists = session.query(data.Artist).filter_by(
            name=artist
            )
        if artists.count() == 0:
            if artist not in artists_to_add:
                log.debug("Found artist: %s" % artist)
                artists_to_add.append(artist)
            else:
                log.debug("Artist %s already found" % artist)
        else:
            log.debug('Artist exists: %s' % artist)

    if len(artists_to_add) > 0:
        log.debug('Adding artists:')
        for artist in artists_to_add:
            log.debug('  - %s' % artist)
        outcome['discoveries']['artists'] = artists_to_add
    else:
        log.debug("No new artists to add")

    session.add_all([ data.Artist(name=artist) for artist in artists_to_add if artist is not None ])
    session.commit()

    # Scan for uncreated albums and create them
    for tag in scanner.tags:
        album = u''.join(tag.tag['album'])
        artist = u''.join(tag.tag['artist'])
        albums = session.query(data.Album).filter_by(name=album)
        if albums.count() == 0:
            if album not in [ a['name'] for a in albums_to_add ]:
                log.debug("Found album: %s" % album)
                artists = session.query(data.Artist).filter_by(name=artist)
                if artists.count() == 0:
                    log.debug("This should never happen, but an Album, '%s', exists for Artist '%s', that doesn't" % (
                        album, artist))
                else:
                    albums_to_add.append({
                        'name': album,
                        'artist': artists.first().id
                        })
            else:
                log.debug("Album %s already found" % album)
        else:
            log.debug('Album exists: %s' % album)
    if len(albums_to_add) > 0:
        log.debug('Adding albums:')
        for album in albums_to_add:
            log.debug('  - %s' % album['name'])
        outcome['discoveries']['albums'] = albums_to_add
    else:
        log.debug("No new albums to add")

    session.add_all([ data.Album(
        name=album['name'], artist_id=album['artist']
        ) for album in albums_to_add if album is not None ])
    session.commit()

    # Scan for track info to add or update
    for tag in scanner.tags:
        title = u''.join(tag.tag['title'])
        album = u''.join(tag.tag['album'])
        number = int(u''.join(tag.tag['tracknumber']))
        filename = u''.join(tag.filename)

        result = session.query(data.Track).filter_by(
            filename=filename
        )
        if result.count() == 0:
            result = session.query(data.Album).filter_by(
                name=album
            )
            if result.count() > 0:
                tracks_to_add.append({
                    'filename': filename,
                    'name': title,
                    'album': result.first().id,
                    'number': number
                })
            else:
                log.debug("A track exists for an album that doesn't: %s"
                    % album)
        else:
            log.debug("Track exists: %s" % title)

    if len(tracks_to_add) > 0:
        log.debug('Adding tracks:')
        for track in tracks_to_add:
            log.debug('  - %s' % track['name'])
        outcome['discoveries']['tracks'] = tracks_to_add
    else:
        log.debug("No new tracks to add")

    session.add_all([ data.Track(
        filename=track['filename'],
        name=track['name'],
        album_id=track['album'],
        number=track['number']
        ) for track in tracks_to_add if track is not None ])
    session.commit()
    session.close()

    return json.dumps(outcome)

@Authorized(['listener'])
def get_artists(filters={}):
    session = data.session()
    artists = session.query(data.Artist)

    for f in filters:
        if f == "id":
            artists = artists.filter_by(id=filters[f])
        elif f == "name":
            artists = artists.filter(data.Artist.name.like("%%%s%%" % filters[f]))
        else:
            log.debug("Unknown filter: %s" % f)

    artists = artists.order_by(data.Artist.name)

    session.close()

    return artists


@Authorized(['listener'])
def get_albums(filters={}):
    session = data.session()
    albums = session.query(data.Album).join(data.Album.artist)

    for f in filters:
        if f == "id":
            albums = albums.filter(data.Album.id == filters[f])
        elif f == "name":
            albums = albums.filter(data.Album.name.like("%%%s%%" % filters[f]))
        elif f == "artist":
            albums = albums.filter(data.Artist.name.like("%%%s%%" % filters[f]))
        else:
            log.debug("Unknown filter: %s" % f)

    albums = albums.order_by(data.Album.name)

    session.close()

    return albums

@Authorized(['listener'])
def get_tracks(filters={}):
    session = data.session()
    tracks = session.query(data.Track).join(data.Track.album).join(data.Album.artist)

    for f in filters:
        if f == "id":
            tracks = tracks.filter(data.Track.id == filters[f])
        elif f == "artist":
            tracks = tracks.filter(data.Artist.name.like("%%%s%%" % filters[f]))
        elif f == "artist_id":
            tracks = tracks.filter(data.Artist.id == filters[f])
        elif f == "album":
            tracks = tracks.filter(data.Album.name.like("%%%s%%" % filters[f]))
        elif f == "album_id":
            tracks = tracks.filter(data.Album.id == filters[f])
        elif f == "number":
            tracks = tracks.filter(data.Track.number == filters[f])
        elif f == "name":
            tracks = tracks.filter(data.Track.name.like("%%%s%%" % filters[f]))
        else:
            log.debug("Unknown filter: %s" % f)

    tracks = tracks.order_by(data.Track.number)

    session.close()

    return tracks

