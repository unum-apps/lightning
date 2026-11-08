"""
Module for the Lightning API
"""

import json
import sys

import micro_logger

import flask
import flask_restx
import relations_pymysql
import relations_restx
import relations_unifist
import relations_unum

import unum_lightning

WHO = "lightning"
NAME = f"{WHO}-api"

def build():
    """
    Builds the Flask App
    """

    app = flask.Flask(NAME)

    app.logger = micro_logger.getLogger(NAME)
    app.lightning = unum_lightning.SOURCE
    app.unifist = unum_lightning.UNIFIST

    # The config is the routed source's own arguments (unum, local, members if any), passed straight through. The
    # routed source is the one the models name, so every operation on them is routed by the Route rows in the unum
    # schema, which unifist-unum owns and migrates, and ends at the DB source the config names. That DB is the lightning
    # one, named by the models' source, and the unifist schema is unifist-unum's too, for ids and the journal.

    with open("/opt/service/config/unum.json", "r", encoding="utf-8") as unum_file:
        config = json.loads(unum_file.read())

    unum_lightning.Base.HOME = config["unum"]

    api = relations_restx.Api(app)

    with open("/opt/service/secret/mysql.json", "r", encoding="utf-8") as mysql_file:
        mysql = json.loads(mysql_file.read())

    app.sources = [
        relations_pymysql.Source(name, schema=schema.replace('-', '_'), autocommit=True, **mysql)
        for name, schema in [
            (config["local"], app.lightning),
            (app.unifist, app.unifist),
            (relations_unum.UnumBase.SOURCE, relations_unum.UnumBase.SOURCE)
        ]
    ]

    relations_unum.Source(app.lightning, **config)

    app.unum = config["unum"]

    def ping():
        for source in app.sources:
            source.connection.ping(True)

    app.before_request(ping)

    api.add_resource(Health, '/health')

    relations_unifist.attach(api, sys.modules[__name__], unum_lightning.models())

    route(app)

    return app

def route(app):
    """
    Routes this unum's data to this app's DB, once: it's a Route row in the unum schema, which is there already
    because unifist-unum migrates it
    """

    row = {"home": app.unum, "source": app.lightning, "role": "owner", "holder": app.unum}

    if not relations_unum.Route.many(**row).retrieve():
        relations_unum.Route(**row).create()


class Health(flask_restx.Resource):
    """
    Class for Health checks
    """

    def get(self):
        """
        Just return ok
        """
        return {"message": "OK"}
