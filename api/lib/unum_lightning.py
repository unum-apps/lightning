"""
The models Lightning owns
"""

import sys

import relations
import relations_unifist

SOURCE = "lightning"
UNIFIST = relations_unifist.UnifistBase.SOURCE


class Base(relations_unifist.UnifistModel):
    """
    Base class for Lightning models, whose ids come from the Unifist source
    """

    SOURCE = SOURCE
    UNIFIST = UNIFIST


class Bolt(Base):
    """
    An ongoing effort, akin to a project, that gathers unfinished Scats and creates Strikes. It never flushes
    """

    id = str                    # slug of name
    version = int, 1
    home = str, False
    entity_id = str                             # Who owns it
    name = str
    description = str
    what = dict, False                          # Holds the part_of_id and from_id, if any
    from_id = relations.Field(str, inject="what__from_id", none=True)   # The Bolt it broke off from, lineage only

    SLUG = "name"

# A subproject belongs to and rolls up into the Bolt it is part of. A Bolt that broke off another stands on its own

relations.OneToMany(
    Bolt, Bolt, parent_child_attr="parts", child_parent_attr="part_of", child_parent_ref="part_of_id",
    child_inject="what"
)


class Rod(Base):
    """
    A stored selection and an action, with the inputs it takes. Striking it creates a Strike
    """

    id = str                    # slug of name
    version = int, 1
    home = str, False
    entity_id = str                             # Who owns it
    name = str
    selection = dict, False                     # What it picks out
    act = dict, False                           # The action: what it does with what it picks, a name for the field
                                                # because action is reserved
    input = dict, False                         # What it takes, such as a location
    what = dict, False

    SLUG = "name"


class Strike(Base):
    """
    A todo: created, in progress, and done at the end
    """

    id = str
    version = int, 1
    home = str, False
    entity_id = str                             # Who owns it
    description = str                           # What is to be done
    state = ["created", "in progress", "done"]
    what = dict, False                          # Holds the bolt_id, rod_id and flush_id, if any

relations.OneToMany(Bolt, Strike, child_inject="what")
relations.OneToMany(Rod, Strike, child_inject="what")


class StrikeScat(Base):
    """
    A Scat a Strike is tied to, which Cumulus owns, and the Strike flushes when it is done
    """

    id = str
    strike_id = str
    scat_id = str                               # The id of the Scat
    version = int, 1
    home = str, False
    what = dict, False

    UNIQUE = ["strike_id", "scat_id"]

relations.OneToMany(Strike, StrikeScat)


class Forecast(Base):
    """
    Something expected, which a Scat can violate
    """

    id = str                    # slug of name
    version = int, 1
    home = str, False
    entity_id = str                             # Who owns it
    name = str
    description = str
    what = dict, False                          # Holds the bolt_id, if any

    SLUG = "name"

relations.OneToMany(Bolt, Forecast, child_inject="what")


class ForecastScat(Base):
    """
    A Scat that violates a Forecast, which Cumulus owns
    """

    id = str
    forecast_id = str
    scat_id = str                               # The id of the Scat
    version = int, 1
    home = str, False
    what = dict, False

    UNIQUE = ["forecast_id", "scat_id"]

relations.OneToMany(Forecast, ForecastScat)


def models():
    """
    The Lightning models, and the Sequence, Slug and Journal tables they take their ids and journal from
    """

    return (
        relations.models(relations_unifist, relations_unifist.UnifistBase) +
        relations.models(sys.modules[__name__], Base)
    )
