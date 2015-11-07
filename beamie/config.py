#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Primary configuration for Beamie"""
import logging
import logging.config
import os
import yaml

class Config(dict):
    """Dictionary of options built from a config file"""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        if 'config_file' in kwargs:
            self.parse_file(kwargs['config_file'])
        else:
            self.parse_file()

    def parse_file(self, filename=None):
        if filename is None:
            filename = os.getcwd() + "/beamie.yml"
        data = yaml.load(open(filename, 'r'))

        if not isinstance(data, dict):
            raise Exception("Could not parse the config file at {}".format(
                filename
            ))

        deep_merge(self, data)

    def configure_logging(self):
        """Configures application logging"""
        log_config = {
            'version' : 1,
            'formatters' : {
                'simple' : {
                    'format' : CONFIG['logging']['format']
                }
            },
            'handlers' : {
                'console' : {
                    'class' : 'logging.StreamHandler',
                    'level' : CONFIG['logging']['level'],
                    'formatter' : 'simple',
                    'stream' : 'ext://sys.stdout'
                }
            },
            'loggers' : {
                'stdout' : {
                    'level' : CONFIG['logging']['level'],
                    'handlers' : [
                        'console'
                    ],
                    'propagate' : False
                }
            },
            'root' : {
                'level' : CONFIG['logging']['level'],
                'handlers' : [
                    'console'
                ]
            }
        }
    
        try:
            logging.config.dictConfig(log_config)
        except Exception, e:
            log.critical("Could not configure logging")

def deep_merge(base, to_merge):
    """Merges the contents of to_merge into base"""

    for key, value in list(to_merge.items()):
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge(base[key], value)
        else:
            base[key] = value

    return base


CONFIG = Config()
