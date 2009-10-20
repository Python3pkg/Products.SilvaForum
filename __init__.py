# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$


def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('resources', globals())
