#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import logging
import json
import os
import requests as r
import sys

# Point these settings at a running Beamie instance
protocol = 'http'
host = 'localhost'
port = 1337
base_path = '/'

url_base = "%s://%s:%i%s" % (
    protocol, host, port, base_path
    )

base_headers = {
    'User-Agent' : 'Beamie Test Suite'
}

outcome = {
    'failures' : [],
    'successes' : [],
    'token' : False
}

# Establish logging
log = logging.getLogger(__name__)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(funcName)s: %(message)s'))
log_handler.setLevel(logging.DEBUG)
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

def auth_with_no_data():
    log.debug("")
    headers = base_headers
    try:
        headers.pop('x-auth-token')
    except KeyError:
        pass
    
    resp = r.post(url_base + 'tokens', headers=headers)

    try:
        assert resp.status_code == 400
        outcome['successes'].append("auth_with_no_data")
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_no_data: Status code is %i; we expect %i" % (
            resp.status_code, 400 ))

def auth_with_no_password():
    log.debug("")
    headers = base_headers
    headers['content-type'] = 'application/json'
    
    resp = r.post(url_base + 'tokens',
                  headers=headers,
                  data=json.dumps({
                    "user" : "root"
                  }))

    try:
        assert resp.status_code == 400
        outcome['successes'].append('auth_with_no_password')
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_no_password: Status code is %i; we expect %i" % (
            resp.status_code, 400))
            
def auth_with_no_username():
    log.debug("")
    headers = base_headers
    headers['Content-Type'] = 'application/json'
    
    resp = r.post(url_base + 'tokens',
                  headers=headers,
                  data=json.dumps({
                    "password" : "adminpass"
                  }))

    try:
        assert resp.status_code == 400
        outcome['successes'].append('auth_with_no_username')
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_no_username: Status code is %i; we expect %i" % (
            resp.status_code, 400))

def auth_with_bad_password():
    log.debug("")
    headers = base_headers
    headers['Content-Type'] = 'application/json'
    
    resp = r.post(url_base + 'tokens',
                  headers=headers,
                  data=json.dumps({
                    "user" : "root",
                    "password" : "fart"
                  }))

    try:
        assert resp.status_code == 401
        outcome['successes'].append('auth_with_bad_password')
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_bad_password: Status code is %i; we expect %i" % (
            resp.status_code, 401))

def auth_with_bad_username():
    log.debug("")
    headers = base_headers
    headers['Content-Type'] = 'application/json'
    
    resp = r.post(url_base + 'tokens',
                  headers=headers,
                  data=json.dumps({
                    "user" : "herphead",
                    "password" : "adminpass"
                  }))

    try:
        assert resp.status_code == 401
        outcome['successes'].append('auth_with_bad_username')
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_bad_username: Status code is %i, we expect %i" % (
            resp.status_code, 401))


def auth_with_good_credentials():
    log.debug("")
    headers = base_headers
    headers['Content-Type'] = 'application/json'
    
    resp = r.post(url_base + 'tokens',
                  headers=headers,
                  data=json.dumps({
                    "user" : "root",
                    "password" : "adminpass"
                  }))

    try:
        assert resp.status_code == 200
        outcome['token'] = resp.json()['token']
        outcome['successes'].append('auth_with_good_credentials')
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("auth_with_good_credentials: Status code is %i, we expect %i" % (
            resp.status_code, 200))
        return
    except KeyError:
        outcome['failures'].append("auth_with_good_credentials: No token in response.")


def download_track():
    log.debug("")
    if not outcome['token']:
        auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] = outcome['token']
    filename = r.get(url_base + "tracks/4", headers=headers).json()['filename']
    resp = r.get(url_base + "tracks/4/download", headers=headers)

    try:
        assert resp.status_code == 200
        with open('test/output.mp3', 'wb') as fd:
            for chunk in resp.iter_content(100):
                fd.write(chunk)
            fd.close()
    except AssertionError:
        outcome['failures'].append("download_track: Expected status code %i, got %i" % (
                                   200, resp.status_code))
        return

    md5_on_disk = hashlib.md5()
    md5_of_dl = hashlib.md5()
    
    fd = open('test/output.mp3', 'rb')
    chunk = fd.read(128)
    while chunk != '':
        md5_of_dl.update(chunk)
        chunk = fd.read(128)
    fd.close()

    fd = open(filename, 'rb')
    chunk = fd.read(128)
    while chunk != '':
        md5_on_disk.update(chunk)
        chunk = fd.read(128)
    fd.close()

    try:
        assert md5_on_disk.hexdigest() == md5_of_dl.hexdigest()
        outcome['successes'].append("download_track")
        log.debug('OK')
    except AssertionError:
        failure = "download_track: md5sum of downloaded track does not match md5sum of original file."
        failure += "Original: %s; Downloaded: %s" % (md5_on_disk.hexdigest(), md5_of_dl.hexdigest())
        outcome['failures'].append(failure)
        return
    finally:
        os.remove('test/output.mp3')


def get_tracks():
    log.debug("")
    
    if not outcome['token']:
        auth_with_good_credentials()
    
    headers = base_headers
    headers['x-auth-token'] = outcome['token']

    # Get all tracks
    resp = r.get(url_base + "tracks", headers=headers)

    try:
        assert resp.status_code == 200
        assert len(resp.json()) == 23
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_tracks (all): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))

    # Get track by id
    resp = r.get(url_base + "tracks/4", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()
        assert j['name'] == u'Silly Boy'
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_tracks (id): Expected status code %i, got %i; Body: %s" % (
                                    200, resp.status_code, resp.text ))

    # Get track by filters (artist like 'ell', album like 'night', 4th track)
    resp = r.get(url_base + "tracks?number=4&album=night&artist=ell", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()[0]
        assert j['name'] == "Artificial Joy"
        assert j['album'] == "Nightwavs"
        assert j['artist'] == "The Easton Ellises"
        log.debug("number/album/artist filters OK")
    except AssertionError:
        failure = "get_tracks (number/album/artist): Expected status code %i, got %i; Body: %s" % (
                   200, resp.status_code, resp.text )
        outcome['failures'].append(failure)

    # Get track by filters (album id 4 and track name like 'an')
    resp = r.get(url_base + "tracks?album_id=1&name=an", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()
        assert len(j) == 2
        log.debug("album_id/name filters OK")
    except AssertionError:
        failure = "get_tracks (album_id/name): Expected status code %i, got %i; Body: %s" % (
                   200, resp.status_code, resp.text )
        outcome['failures'].append(failure)

    # Get tracks by one artist with artist id
    resp = r.get(url_base + "tracks?artist_id=1", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()
        assert len(j) == 4
        log.debug("artist_id filter OK")
    except AssertionError:
        failure = "get_tracks (artist_id): Expected status code %i, got %i; " % (
                   200, resp.status_code )
        outcome['failures'].append(failure)


def get_albums():
    log.debug("")
    if not outcome['token']:
        auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] = outcome['token']

    # Get all albums
    resp = r.get(url_base + "albums", headers=headers)

    try:
        assert resp.status_code == 200
        assert len(resp.json()) == 7
        outcome['successes'].append("get_albums (all)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_albums (all): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))

    # Get album by id (id 3, "These Nights" by Modern Pitch)
    resp = r.get(url_base + "albums/3", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()
        assert j['name'] == "These Nights"
        assert j['artist'] == "Modern Pitch"
        outcome['successes'].append("get_albums (id)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_albums (id): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))

    # Get album by filters (name like 'o' and artist like 'l'))
    resp = r.get(url_base + "albums?name=o&artist=l", headers=headers)

    try:
        assert resp.status_code == 200
        j = resp.json()
        assert len(j) == 2
        outcome['successes'].append("get_albums (name/artist)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_albums (name/artist): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))


def get_artists():
    log.debug("")
    if not outcome['token']:
        auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] = outcome['token']

    # Get all artists
    resp = r.get(url_base + "artists", headers=headers)

    try:
        assert resp.status_code == 200
        assert len(resp.json()) == 3
        outcome['successes'].append("get_artists (all)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_artists (all): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))
        
    # Get artists by name (name like 'pub')
    resp = r.get(url_base + "artists?name=pub", headers=headers)

    try:
        assert resp.status_code == 200
        assert resp.json()[0]['name'] == "Publisher"
        outcome['successes'].append("get_artists (name)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_artists (name): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))
        
    # Get artists by id (2)
    resp = r.get(url_base + "artists/2", headers=headers)

    try:
        assert resp.status_code == 200
        assert resp.json()['name'] == "Modern Pitch"
        outcome['successes'].append("get_artists (id)")
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("get_artists (id): Expected status code %i, got %i; Body: %s" % (
                                   200, resp.status_code, resp.text ))
        

def scan_with_valid_auth():
    log.debug("")
    auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] == outcome['token']

    resp = r.post(url_base + "scan", headers=headers)

    try:
        assert resp.status_code == 200
        log.debug(resp.text)
        outcome['successes'].append('scan_with_valid_auth')
        log.debug('OK')
    except AssertionError:
        outcome['failures'].append("scan_with_valid_auth: Expected status code %i, got %i" % (
                  200, resp.status_code ))

def validate_good_token_with_good_x_auth_token():
    log.debug("")
    auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] = outcome['token']

    resp = r.get("%stokens/%s" % ( url_base, outcome['token'] ),
                 headers=headers)

    try:
        assert resp.status_code == 200
        body = resp.json()
        assert 'user' in body
        assert 'roles' in body['user']
        outcome['successes'].append("validate_good_token_with_good_x_auth_token")
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("validate_good_token_with_good_x_auth_token: Expected status code %i, got %i; expected valid JWT, got %s" % (
                  200, resp.status_code, resp.text ))
        return



def validate_good_token_with_bad_x_auth_token():
    log.debug("")
    auth_with_good_credentials()
    headers = base_headers
    headers['x-auth-token'] = "this isn't real whatis reality"

    resp = r.get("%stokens/%s" % ( url_base, outcome['token'] ),
                 headers=headers)

    try:
        assert resp.status_code == 401
        outcome['successes'].append("validate_good_token_with_bad_x_auth_token")
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("validate_good_token_with_bad_x_auth_token: Expected status code %i, got %i" % (
                  401, resp.status_code ))
        return


def validate_good_token_with_no_x_auth_token():
    log.debug("")
    auth_with_good_credentials()

    headers = base_headers
    if 'x-auth-token' in headers:
        headers.pop('x-auth-token')

    resp = r.get("%stokens/%s" % ( url_base, outcome['token'] ),
                 headers=headers)

    try:
        assert resp.status_code == 401
        outcome['successes'].append("validate_good_token_with_no_x_auth_token")
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("validate_good_token_with_no_x_auth_token: Expected status code %i, got %i" % (
                  401, resp.status_code ))
        return


def validate_bad_token_with_good_x_auth_token():
    log.debug("")
    auth_with_good_credentials()

    headers = base_headers
    headers['x-auth-token'] = outcome['token']

    resp = r.get("%stokens/%s" % ( url_base, 'teh worst token' ),
                 headers=headers)

    try:
        assert resp.status_code == 404
        outcome['successes'].append("validate_bad_token_with_good_x_auth_token")
        log.debug("OK")
    except AssertionError:
        outcome['failures'].append("validate_bad_token_with_good_x_auth_token: Expected status code %i, got %i" % (
                  200, resp.status_code ))
        return


# Output
def print_outcome():
    print
    print("#### Test Results")
    print
    print("  ## Successful")
    for success in outcome['successes']:
        print("     %s" % success)
    print
    print("  ## Failures")
    if len(outcome['failures']) == 0:
        print("     No failures!")
    else:
        for failure in outcome['failures']:
            print("     %s" % failure)


# Test groups
def run_data_tests():
    get_tracks()
    get_albums()
    get_artists()
    download_track()

def run_scan_tests():
    scan_with_valid_auth()

def run_token_tests():
    auth_with_no_data()
    auth_with_no_password()
    auth_with_no_username()
    auth_with_bad_password()
    auth_with_bad_username()
    auth_with_good_credentials()
    validate_good_token_with_good_x_auth_token()
    validate_good_token_with_bad_x_auth_token()
    validate_good_token_with_no_x_auth_token()
    validate_bad_token_with_good_x_auth_token()


# All tests
def run_all():
    run_token_tests()
    run_scan_tests()
    run_data_tests()
    print_outcome()

if __name__ == "__main__":
    run_all()
    log.debug("Tests complete.")
