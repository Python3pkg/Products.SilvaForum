# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
"""Provides a function called 'translate' that *must* be imported as '_':

    from Products.SilvaMailing.i18n import translate as _

and will provide a MessageIDFactory that returns MessageIDs for
i18n'ing Product code and Python scripts.
"""
from zope.i18nmessageid import MessageFactory

translate = MessageFactory('silvaforum')
