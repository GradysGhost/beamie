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

### Clone this Repo

    git clone git@github.com:GradysGhost/beamie.git /opt/beamie

### PYTHONPATH
To do just about anything, you need `PYTHONPATH` set to the root of the git
repo. So maybe...

    cd /opt/beamie
    export PYTHONPATH=$PWD

### Dependencies

Install Beamie's dependencies. MySQL support depends on the `mysql-python` pip
package, which itself depends on some MySQL client libraries. You'll need to
install them first.

#### Debian/Ubuntu

    sudo apt-get install libmysqlclient-dev

#### CentOS

    sudo yum install mysql-devel

And then you need to install some python packages:

    pip install -r requirements.txt

### Build a Clean Database

Don't forget to initialize a clean database before starting Beamie up.

#### SQLite

    python db-init.py sqlite:///data/beamie.db

#### MySQL

    python db-init.py mysql://username:password@host:3306/schema

Also don't forget to set the `db_string` value in the config file (`beamie.yml`
by default) to the connetion string you used to create the database.

### Run Beamie

    python runbeamie.py


## Configuration

### Command Line Arguments

    $ python runbeamie.py  -h
    usage: runbeamie.py [-h] [-c [CONFIG_FILE]] [-t]
    
    Run the Beamie server
    
    optional arguments:
      -h, --help            show this help message and exit
      -c [CONFIG_FILE], --config [CONFIG_FILE]
                            Path to Beamie's config file
      -t, --test            Run full tests and quit

### Config File Options

 * `db_string` - The database connection string.
 * `allowed_extensions` - The media scanner will only pay attention to media
   files that have these extensions.
 * `media_paths` - A list of directories where Beamie looks for media.
 * `bind_address`- The IP address to bind to.
 * `bind_port` - The port to listen on.
 * `token_expiry` - The number of seconds that a new token is valid for.
 * `logging` - A [Python logger configuration object]
   (https://docs.python.org/2/library/logging.config.html)


## Test Data Credit

The media files in `test/media` are graciously provided by artists who
release their art under a Creative Commons license that allows us to store
and redistribute the music for our test purposes. A debt of gratitude is owed
to these folks for their generosity:

 * [Modern Pitch](https://www.jamendo.com/artist/444576/modern-pitch)
 * [Publisher](https://www.jamendo.com/artist/457443/publisher)
 * [The Easton Ellises](https://www.jamendo.com/artist/370143/the-easton-ellises)

