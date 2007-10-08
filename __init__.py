# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Silva

import os
from Products.Silva.fssite import registerDirectory

def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('resources', globals())
    path = os.path.join('emoticons', 'smilies')
    registerDirectory(path, globals())
