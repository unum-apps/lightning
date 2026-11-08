# Changelog

## 0.2.0

- The gui: a Flow page to strike a Rod (pick it, give the inputs it asks for, and a Strike is made) and to work the open Strikes from created to in progress to done. The routes that take an id now match string ids like `eat-well:bolt.lightning:test`, which the numeric ones could not, so retrieve and update work for every Term. `make test` runs the gui's tests (node:test) and the Jenkinsfile runs them (unum-apps/lightning#3).

## 0.1.0

- The scaffold, in the layout of Cumulus (unum-apps/cumulus 0.2.2): an `api` with the Unifist base and its journal, a `gui`, the kubernetes folders, the Tiltfile, the Jenkinsfile, the Makefiles and the release scripts. (unum-apps/lightning#1)
- The models: `Bolt` (with `part_of_id` and `from_id`), `Rod` (a stored selection, `act` and `input`), `Strike` (a todo that is created, in progress or done, with an optional `bolt_id` and `rod_id`), `Forecast` (with an optional `bolt_id`), and the ties `StrikeScat` and `ForecastScat` to Scats, which Cumulus owns. Every one has an `entity_id` string for its owner, and the ids are strings (unum-apps/lightning#2).
