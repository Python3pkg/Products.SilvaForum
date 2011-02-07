# Copyright (c) 2007-2011 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from Products.Silva.install import add_helper, pt_add_helper
from five import grok
from silva.app.subscriptions.interfaces import ISubscriptionService
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller, roleinfo
from zope import component
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

silvaconf.extensionName('SilvaForum')
silvaconf.extensionTitle('Silva Forum')


class IExtension(Interface):
    """Silva Forum extension.
    """


class SilvaForumInstaller(DefaultInstaller):
    not_globally_addables = ['Silva Forum Topic', 'Silva Forum Comment']
    default_permissions = {'Silva Forum': roleinfo.EDITOR_ROLES}
    metadata = {('Silva Forum Topic', 'Silva Forum Comment'):
                    ('silva-content', 'silva-extra', 'silvaforum-item'),
                ('Silva Forum',):
                    ('silva-content', 'silva-extra', 'silva-layout'),
                ('Silva Forum', 'Silva Forum Topic'):
                    ('silvaforum-forum',)}

    def install_custom(self, root):
        self.configure_metadata(root, self.metadata, globals())

        # Add a subscription service
        subscriptions = component.queryUtility(ISubscriptionService)
        if subscriptions is None:
            factory = root.manage_addProduct['silva.app.subscriptions']
            factory.manage_addSubscriptionService()

    def uninstall_custom(self, root):
        self.unconfigure_metadata(root, self.metadata)


install = SilvaForumInstaller('SilvaForum', IExtension)

@grok.subscribe(ISubscriptionService, IObjectCreatedEvent)
def add_forum_notification_tempate(service, event):
    add_helper(
        service, 'forum_event_template.pt', globals(), pt_add_helper, True)
