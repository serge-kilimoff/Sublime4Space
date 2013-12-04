#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
from __future__ import unicode_literals, print_function, division
import os
import site

__author__ = "Serge Kilimoff-Goriatchkine"
__email__ = "serge.kilimoff@gmail.com"
__license__ = 'MIT license'


# append current directory to paths system
current_directory = os.path.split(__file__)[0]
site.addsitedir(current_directory)
