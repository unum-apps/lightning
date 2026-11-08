import unittest
import unittest.mock

import relations
import relations.unittest
import relations_pymysql
import relations_unifist
import relations_unum

import service
import unum_lightning

import glob
import json
import os
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

MODELS = ["Journal", "Sequence", "Slug"]

SECRET = '{"host": "%s", "user": "root", "password": ""}' % os.environ["MYSQL_HOST"]
CONFIG = '{"unum": "test", "local": "lightning-test", "cert": ["/certs/client/tls.crt", "/certs/client/tls.key"], "verify": "/certs/roots/ca.crt"}'

def opened(path, *args, **kwargs):
    """
    Stands in for open, giving the config file its unum and everything else the secret
    """

    return unittest.mock.mock_open(read_data=CONFIG if path.endswith("unum.json") else SECRET)(path, *args, **kwargs)

class Testrestx(relations.unittest.TestCase):

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', side_effect=opened)
    def setUp(self, mock_open):

        # Building the app writes the Route, so the databases and tables are there first, made with sources of the
        # same names, which building the app then makes again

        mysql = json.loads(SECRET)

        by_name = {
            name: relations_pymysql.Source(name, schema=schema, autocommit=True, **mysql)
            for name, schema in [("lightning-test", "lightning"), ("unifist", "unifist"), ("unum", "unum")]
        }

        for source in by_name.values():
            source.connection.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{source.schema}`")

        # Lightning has no tables of its own yet, so there is no DDL to load into the DB source behind the routed one

        # The unifist and unum tables belong to unifist-unum, so they're made from the base models, not from DDL here

        for model in relations.models(relations_unifist, relations_unifist.UnifistBase):
            by_name["unifist"].execute(model.define())

        for model in relations.models(relations_unum, relations_unum.UnumBase):
            by_name["unum"].execute(model.define())

        self.app = service.build()
        self.api = self.app.test_client()

    def tearDown(self):

        for source in self.app.sources:
            source.connection.cursor().execute(f"DROP DATABASE IF EXISTS `{source.schema}`")


class TestModels(unittest.TestCase):

    def test_models(self):

        self.assertEqual(sorted(model.__name__ for model in unum_lightning.models()), MODELS)

    def test_home(self):

        # The home a query names has to be the home field, which routing reads to know which unums to ask. A relation
        # or any other attribute of the same name would take the filter for itself, so the query would be for every
        # unum and two unums joined to each other would ask each other for ever

        for model in unum_lightning.models():

            if "home" not in model.thy()._fields._names:
                continue

            with self.subTest(model=model.__name__):
                query = model.many(home__in=["away"])
                self.assertEqual(query._record._names["home"].criteria, {"in": ["away"]})
                self.assertEqual(query._ties, {})


class TestAPI(Testrestx):

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', side_effect=opened)
    def test_build(self, mock_open):

        app = service.build()

        self.assertEqual(app.name, "lightning-api")
        self.assertEqual(app.lightning, "lightning")
        self.assertEqual(app.unifist, "unifist")
        self.assertEqual([source.name for source in app.sources], ["lightning-test", "unifist", "unum"])
        self.assertEqual(unum_lightning.Base.HOME, "test")

        routed = relations.source("lightning")

        self.assertIsInstance(routed, relations_unum.Source)
        self.assertEqual(routed.unum, "test")
        self.assertEqual(routed.local, "lightning-test")

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', side_effect=opened)
    def test_secure(self, mock_open):

        # The config's cert and verify are what each unum's calls to another present and verify with, so a route
        # to an https url works against a unum that checks client certificates and has its own CA

        rest = relations.source(self.app.lightning).reach("away", "https://away.test")
        session = relations.source(rest).session

        self.assertEqual(session.cert, ("/certs/client/tls.crt", "/certs/client/tls.key"))
        self.assertEqual(session.verify, "/certs/roots/ca.crt")

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', side_effect=opened)
    def test_route(self, mock_open):

        routes = lambda: relations_unum.Route.many(home="test", source="lightning").retrieve()

        # Building the app in setUp wrote the Route

        self.assertEqual(len(routes()), 1)
        self.assertEqual(routes()[0].role, "owner")
        self.assertEqual(routes()[0].holder, "test")
        self.assertEqual(routes()[0].url, "")

        # Building it again doesn't write another

        service.build()

        self.assertEqual(len(routes()), 1)

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', side_effect=opened)
    def test_route_last(self, mock_open):

        seen = []

        def route(app):
            seen.append({
                "sources": [source.name for source in app.sources],
                "registered": all(relations.source(source.name) is source for source in app.sources),
                "routed": relations.source("lightning"),
                "health": "/health" in [rule.rule for rule in app.url_map.iter_rules()],
                "models": "/model/journal" in [rule.rule for rule in app.url_map.iter_rules()]
            })

        with unittest.mock.patch("service.route", side_effect=route) as mocked:
            service.build()

        # The Route is written once, and last: the lightning DB source, the unifist source and the unum source are made and
        # registered, the routed source is made and named by the models, and the resources are attached, all before it

        mocked.assert_called_once()
        self.assertEqual(seen[0]["sources"], ["lightning-test", "unifist", "unum"])
        self.assertTrue(seen[0]["registered"])
        self.assertIsInstance(seen[0]["routed"], relations_unum.Source)
        self.assertEqual(seen[0]["routed"].local, "lightning-test")
        self.assertTrue(seen[0]["health"])
        self.assertTrue(seen[0]["models"])

    def test_migrations(self):

        local = relations.source("lightning-test")
        cursor = local.connection.cursor()

        for migration in sorted(glob.glob("ddl/lightning/mysql/migration-*.sql")):

            stamp = migration.rsplit("migration-", 1)[-1].split(".")[0]

            cursor.execute("DROP DATABASE IF EXISTS `lightning`")
            cursor.execute("CREATE DATABASE IF NOT EXISTS `lightning`")

            try:
                local.load(f"ddl/lightning/mysql/definition-{stamp}.sql")
                local.load(migration)
            except Exception as exception:
                print(stamp)
                raise exception

class TestHealth(Testrestx):

    def test_get(self):

        self.assertStatusValue(self.api.get("/health"), 200, "message", "OK")


class TestModelAPI(Testrestx):

    def test_models(self):

        response = self.api.get("/model")

        self.assertEqual(response.status_code, 200, response.json)
        self.assertEqual(sorted(model["title"] for model in response.json["models"]), MODELS)

    def test_empty(self):

        for model in self.api.get("/model").json["models"]:
            response = self.api.get(f"/model/{model['singular']}")
            self.assertEqual(response.status_code, 200, model["singular"])
            self.assertEqual(response.json[model["plural"]], [], model["singular"])

    def test_journal(self):

        response = self.api.get("/model/journal")

        self.assertEqual(response.status_code, 200, response.json)
        self.assertEqual(response.json["journals"], [])
