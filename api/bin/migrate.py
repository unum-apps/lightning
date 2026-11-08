#!/usr/bin/env python

import json

import micro_logger

import relations
import relations_pymysql

import unum_lightning

logger = micro_logger.getLogger("lightning-api")

with open("/opt/service/secret/mysql.json", "r", encoding="utf-8") as mysql_file:
    mysql = json.loads(mysql_file.read())

migrations = relations.Migrations()

# The unifist schema is migrated by unifist-unum
for name in [unum_lightning.SOURCE]:

    schema = name.replace('-', '_')

    source = relations_pymysql.Source(name, schema=schema, autocommit=True, **mysql)

    source.connection.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{schema}`")

    logger.info("migrations", extra={"source": name, "migrated": migrations.apply(name)})
