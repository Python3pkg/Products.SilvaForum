# Copyright (c) 2007 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python


from zope.interface import implements

from AccessControl import getSecurityManager, Unauthorized

from interfaces import IForumSecurityPolicy

minimal_add_role = 'Authenticated'

class DefaultSecurityPolicy(object):

    implements(IForumSecurityPolicy)

    def __init__(self, context):
        self.context = context

    def _authenticated_can_add(self):
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('Sorry you need to be authorized to use this '
                               'forum')

    def can_add_post(self):
        self._authenticated_can_add()
        return True

    def can_add_topic(self):
        self._authenticated_can_add()
        return True
