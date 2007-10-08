# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from Products.Silva.install import add_fss_directory_view
import os

def install(root):
    # install the views directory into service_views
    add_fss_directory_view(root.service_views,
                           'SilvaForum', __file__, 'views')
    add_fss_directory_view(root.service_resources,
                           'SilvaForum', __file__, 'resources')
    add_fss_directory_view(root, 'service_smilies',
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'emoticons', 'hack')),
                           'smilies')

    root.manage_permission('Add Silva Forums',
                           ['Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Forum Threads',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    # XXX needs to be changed to unauthorized or sth, I guess...
    root.manage_permission('Add Silva Forum Comments',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])

    reg = root.service_view_registry

    # define metadata sets
    root.service_metadata.addTypesMapping(
        ('Silva Forum', 'Silva Forum Thread', 'Silva Forum Comment'),
        ('silva-content', 'silva-extra'))
    root.service_metadata.initializeMetadata()
    
    # edit
    reg.register('edit', 'Silva Forum',
                 ['edit', 'Container', 'Folder', 'Forum'])
    reg.register('edit', 'Silva Forum Thread',
                 ['edit', 'Container', 'Folder', 'Thread'])
    reg.register('edit', 'Silva Forum Comment',
                 ['edit', 'Content', 'Comment'])

    # add
    reg.register('add', 'Silva Forum', ['add', 'Forum'])
    reg.register('add', 'Silva Forum Thread', ['add', 'Thread'])
    reg.register('add', 'Silva Forum Comment', ['add', 'Comment'])

    # public is done from Five views

    configureAddables(root)
    
def uninstall(root):
    reg = root.service_view_registry
    reg.unregister('edit', 'Silva Forum')
    reg.unregister('edit', 'Silva Forum Thread')
    reg.unregister('edit', 'Silva Forum Comment')
    reg.unregister('add', 'Silva Forum')
    reg.unregister('add', 'Silva Forum Thread')
    reg.unregister('add', 'Silva Forum Comment')

    root.service_views.manage_delObjects(['SilvaForum'])
    root.service_resources.manage_delObjects(['SilvaForum'])

def configureAddables(root):
    """Make sure the right items are addable in the root"""
    non_addables = ('Silva Forum Thread',
                    'Silva Forum Comment')
    addables = ('Silva Forum',)
    current_addables = root.get_silva_addables_allowed_in_publication()
    new_addables = []
    for a in current_addables:
        if a not in non_addables:
            new_addables.append(a)
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_publication(new_addables)

def is_installed(root):
    return hasattr(root.service_views, 'SilvaForum')

