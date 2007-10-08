# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Silva

from Products.Silva.fssite import registerDirectory

def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('resources', globals())
    registerDirectory('emoticons/smilies', globals())
