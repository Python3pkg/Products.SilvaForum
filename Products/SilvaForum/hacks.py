# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ModuleSecurityInfo, getSecurityManager

# XXX I am not responsible for the code below. I have been threated
# not going home if I didn't write something like that.

module_security = ModuleSecurityInfo('Products.SilvaForum.hacks')
module_security.declarePublic('getCurrentContentMetaType')
def getCurrentContentMetaType():
    user = getSecurityManager().getUser()
    model = user.REQUEST.get('model')
    if model is None:
        # Test or well, you are fuck up.
        return 'This is an hack. Do not change this string or test will fail.'
    return model.meta_type
