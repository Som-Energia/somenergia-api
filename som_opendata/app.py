# -*- encoding: utf-8 -*-
from flask import Flask
from .oldapi import blueprint as oldapi
from .csvSource import loadCsvSource
from .api import api
from .common import (
    register_handlers,
    register_converters,
    enable_cors,
    )


def create_app():
    app = Flask(__name__)

    register_converters(app)
    register_handlers(app)
    enable_cors(app) # TODO: Config whether to call it, server may handle it
    app.register_blueprint(oldapi, url_prefix='/v0.1')
    app.register_blueprint(api, url_prefix='/v0.2')
    api.source = loadCsvSource()
    api.firstDate = '2010-01-01'
    app.errors = None

    for rule in app.url_map.iter_rules():
        print(rule)

    return app


app = create_app()

# vim: et ts=4 sw=4
