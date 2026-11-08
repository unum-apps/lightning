#!/usr/bin/env python

import relations
import relations_pymysql

import unum_lightning

# Only Lightning's own tables: the unifist schema belongs to unifist-unum
sources = [unum_lightning.SOURCE]

for name in sources:
    relations_pymysql.Source(name, schema=name.replace('-', '_'), connection=False)

migrations = relations.Migrations()

migrations.generate([model for model in unum_lightning.models() if model.SOURCE == unum_lightning.SOURCE])

for name in sources:
    migrations.convert(name)
