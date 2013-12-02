#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
from __future__ import unicode_literals, print_function, division

from indent_tokens import OpenToken, CloseToken, BlockToken, InlineToken, WhitespaceToken, TextToken

__author__ = "Serge Kilimoff-Goriatchkine"
__email__ = "serge.kilimoff@gmail.com"


############################################################################
# GRAMMARY RULES
############################################################################
def serialize_open_tag(token):
    if isinstance(token.preceding, TextToken):
        return token.data
    return super(token.__class__, token).__unicode__()


def serialize_close_tag(token):
    if isinstance(token.preceding, OpenToken):
        return token.data
    if isinstance(token.preceding, TextToken):
        return token.data
    return super(token.__class__, token).__unicode__()


def serialize_text(token):
    if isinstance(token.preceding, (OpenToken, CloseToken)):
        return token.data
    return super(token.__class__, token).__unicode__()



XML_GRAMMAR = {
    OpenToken : serialize_open_tag,
    CloseToken : serialize_close_tag,
    TextToken : serialize_text,
}



# Ce motif est utilisé dans les regex qui suivent afin de trouver ce qui correspond
# à une balise xml correctement formées.
# Voir http://fr.wikipedia.org/wiki/Xml#Les_balises pour plus d'informations
# _TEMPLATE_ELEMENT = r"%(exclude)s(?::%(exclude)s)?" % \
#         {'exclude' : r"""[^%(tag_exclude)s0-9\-][^%(tag_exclude)s]*""" % \
#             {'tag_exclude' : r"""!"#$%%&'()*+,/;<=>\?@\[\]\\^`{|}~\s"""}}

# _TEMPLATE_STRING = r"""(?P<quotes>['"]).*?\g<quotes>"""

# _OPENING_TAG = r"""<%(element)s(?:\s*%(element)s=%(string)s)*>""" % {'element' : _TEMPLATE_ELEMENT, 'string' : _TEMPLATE_STRING}
# _CLOSING_TAG = r"""</%(element)s>""" % {'element' : _TEMPLATE_ELEMENT}
# _AUTOCLOSING_TAG = r"""<%(element)s(?:\s*%(element)s=%(string)s)*/>""" % {'element' : _TEMPLATE_ELEMENT, 'string' : _TEMPLATE_STRING}

# _OPENING_TAG = r"""<%(element)s[^>]+>""" % {'element':_TEMPLATE_ELEMENT}



############################################################################
# LEXICON
############################################################################
XML_LEXICON = {
    r"\s*\n+\s*" : WhitespaceToken,
    r"<[^/!][^>]*[^/]?>" : OpenToken,
    r"</[^>]*[^/]>" : CloseToken,
    r"<[^/!][^>]*/>" : InlineToken,
    r"<!--.*?-->" : BlockToken,
    r"<\?.*?\?>" : BlockToken,
    r"<!DOCTYPE.*?>" : BlockToken,
}
