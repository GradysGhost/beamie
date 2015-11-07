#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Runs the Beamie app"""

# Installed module imports
import argparse
import logging as log
# import logging.config
import os

# Local imports
from beamie import app
from beamie.config import CONFIG
from multiprocessing import Process
from test import test

# Some helper functions to get the app up and running
def create_parser():
    """Creates the argparse object so we can read config values from the CLI"""
    parser = argparse.ArgumentParser(description="Run the Beamie server")
    parser.add_argument(
        '-c',
        '--config',
        nargs='?',
        default=os.getcwd() + "/beamie.yml",
        type=str,
        help="Path to Beamie's config file",
        dest="config_file"
    )
    parser.add_argument(
        '-t',
        '--test',
        action='store_true',
        help="Run full tests and quit",
        dest="test"
    )
    return parser


def configure_application():
    """Parses arguments and reads in a config"""
    parser = create_parser()
    opts = parser.parse_args()
    CONFIG.parse_file(opts.config_file)
    CONFIG.configure_logging()
    return opts


def run_server():
    app.run(host=CONFIG['bind_address'], port=CONFIG['bind_port'])

def main():
    """Entry point"""
    # Get configs read and start logging
    opts = configure_application()

    log.info("Beamie initializing...")
    log.info("Logging started at log level: %s", CONFIG['logging']['level'])

    if opts.test:
        server = Process(target=run_server)
        server.start()
        test.run_all()
        server.terminate()
        server.join()
    else:
        run_server()

if __name__ == "__main__":
    main()
