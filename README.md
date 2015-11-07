# Beamie

Beamie is a REST API aimed at providing you with remote access to your media
from anywhere with an internet connection. Its primary features include:

 * Multi-user support
 * Some standard media player features such as media organization and
   playlisting.
 * Arbitrary semantic tagging of artists, albums, and tracks.
 * Query-based playlisting (think: "Shuffle all songs tagged 'summer',
   released after 1975, and which are not by The Cars.")
 * Data storage in any relational database, including SQLite for local storage
   and MySQL/PostgreSQL for more distributed setups.
 * A plugin interface for extending the API.
 * A built-in client that allows users to connect their Beamie server to other
   Beamie servers and aggregate responses from those servers into thier server's
   responses, creating a network of Beamie servers able to serve media to all
   its connected users.

## Aims and Goals

Beamie has some philosophical goals:

 * Software freedom
 * Modern REST API design as described in Mark Masse's fantasic
   [Rest API Design Rulebook](https://library.oreilly.com/book/0636920021575/rest-api-design-rulebook/toc).
 * Decoupling of data storage, logic, and presentation
 * Extensibility
 * Seamless connectivity with other Beamie instances

To exemplify this project's goals by contrast, see the open source project
[Subsonic](https://www.subsonic.org/). Subsonic is pretty cool, and I don't
want to be too hard on it, especially considering I've used it myself for a
very long time, but it has a number of flaws not easily remedied by contributing
code to that project. Namely:

 * Java
 * The API speaks XML
 * API is tightly coupled with two different web UIs
   * One of those web UIs uses HTML frames and Flash
   * The other is a better design, admittedly, using HTML 5, but it could be
     much better (see [Jamstash](http://jamstash.com))
 * Configuration is buried in obscure Java container options in an init script.
 * Paywall/hackwall between you and streaming to mobile devices
   * Although Subsonic is technically open source, paywalls always strike me as
     disingenuous.
 * Software distributed using .deb and .rpm packages

This project targets these problems thus:

 * Written in Python with the Flask API framework. I suppose we could argue all
   day about the superiority/inferiority of languages and frameworks, but at
   least it's not Java.
 * It is purely an API, with no UI aspirations, leaving the user free to use any
   kind of UI he desires. The REST/JSON interface makes it simple to develop UIs
   in a variety of formats. (Although there is currently no accompanying UI
   project, there will be once this code nears a more usable state.)
 * Because there are no UI requirements, UI developers are free to use any
   media playback tech they desire, including HTML 5, native libraries, or even
   Flash.
 * Server configuration is in a comprehensible YAML file.
 * This product is 100% free as in beer **and** as in speech.
 * Distribution via pip/PyPi.

It is important to note that Beamie is in its infancy, and not all of these
features have been implemented yet. The overall model is consistent with these
goals, however.

## Usage Notes

Don't forget to initialize a clean database before starting Beamie up.

    cd /path/to/beamie
    export PYTHONPATH=$PWD
    python db-init.py sqlite:///data/beamie.db


## Test Data

The media files in `test/media` are graciously provided by artists who
release their art under a Creative Commons license that allows us to store
and redistribute the music for our test purposes. A debt of gratitude is owed
to these folks for their generosity:

 * [Modern Pitch](https://www.jamendo.com/artist/444576/modern-pitch)
 * [Publisher](https://www.jamendo.com/artist/457443/publisher)
 * [The Easton Ellises](https://www.jamendo.com/artist/370143/the-easton-ellises)

