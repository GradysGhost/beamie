#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask

app = flask.Flask(__name__)

from beamie.routes import library, tokens, users
