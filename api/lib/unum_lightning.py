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


def models():
    """
    The Lightning models, and the Sequence, Slug and Journal tables they take their ids and journal from
    """

    return (
        relations.models(relations_unifist, relations_unifist.UnifistBase) +
        relations.models(sys.modules[__name__], Base)
    )
