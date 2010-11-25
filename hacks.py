# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ModuleSecurityInfo, getSecurityManager

module_security = ModuleSecurityInfo('Products.SilvaForum.hacks')
module_security.declarePublic('getCurrentContentMetaType')
def getCurrentContentMetaType():
    user = getSecurityManager().getUser()
    return user.REQUEST['model'].meta_type
