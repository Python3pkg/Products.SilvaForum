# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from AccessControl import allow_module

allow_module('Products.SilvaForum.hacks')

def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('resources', globals())
