#!/usr/bin/envpython
#-*-coding:utf-8-*-

# Normal Python modules
import os
import logging as log

# Our private modules
import beamie.data

from beamie.config import CONFIG
from beamie.lib.tag import Tag

class MediaScanner(object):
    """Scans media and updates the database"""
      
    def __init__(self, paths):
        """Constructor"""
        self.files = self.find_files( [ os.path.abspath(p) for p in paths ] )
        self.tags = list()
      
      
    def find_files(self, paths):
        """Gets the list of files in a directory recursively"""

        all_files = list()
        files = list()
        for loc in paths:
            log.debug("Looking for files in %s" % loc)
            # Make sure loc ends in a /
            if loc[-1] is not '/':
                loc += '/'

            # Get lists of files and directories contained in the provided location
            files = [ loc + f for f in os.listdir(loc) if os.path.isfile(loc  + f) ]
            dirs = [ loc + f for f in os.listdir(loc) if os.path.isdir(loc + f) ]

            if len(dirs) > 0:
                all_files.extend(self.find_files(dirs))

            all_files.extend(files)

        for f in files:
            log.debug("Found %s" % f)
            

        return list(set(all_files))

    def scan_files(self):
        allowed_files = list()

        for f in self.files:
            allowed = False
            for ext in CONFIG['allowed_extensions']:
                if f.endswith(ext):
                    allowed_files.append(f)
                    break

        self.tags = [ Tag(f) for f in allowed_files ]

