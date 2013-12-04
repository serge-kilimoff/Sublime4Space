#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
from __future__ import unicode_literals, print_function, division

from tokens import OpenToken, CloseToken, BlockToken, InlineToken, WhitespaceToken, TextToken

__author__ = "Serge Kilimoff-Goriatchkine"
__email__ = "serge.kilimoff@gmail.com"
__license__ = 'MIT license'


CSS_LEXICON = {
    r"\s*\n+\s*" : WhitespaceToken,
    r'/\*.*?\*/' : BlockToken,
    r'\{' : OpenToken,
    r'\}' : CloseToken,
    r'[\w-]+\s*:\s*[^;];' : BlockToken,
}
