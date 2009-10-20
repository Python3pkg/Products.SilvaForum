# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from Products.Silva.install import add_fss_directory_view
from Globals import package_home
import os

def install(root):
    # install the views directory into service_views
    add_fss_directory_view(root.service_views,
                           'SilvaForum', __file__, 'views')
    add_fss_directory_view(root.service_resources,
                           'SilvaForum', __file__, 'resources')

    root.manage_permission('Add Silva Forums',
                           ['Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Forum Topics',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    # XXX needs to be changed to unauthorized or sth, I guess...
    root.manage_permission('Add Silva Forum Comments',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])

    reg = root.service_view_registry

    # define metadata sets
    root.service_metadata.addTypesMapping(
        ('Silva Forum', 'Silva Forum Topic', 'Silva Forum Comment'),
        ('silva-content', 'silva-extra'))
    root.service_metadata.initializeMetadata()

    # edit
    reg.register('edit', 'Silva Forum',
                 ['edit', 'Container', 'Folder', 'Forum'])
    reg.register('edit', 'Silva Forum Topic',
                 ['edit', 'Container', 'Folder', 'Topic'])
    reg.register('edit', 'Silva Forum Comment',
                 ['edit', 'Content', 'Comment'])

    # add
    reg.register('add', 'Silva Forum', ['add', 'Forum'])
    reg.register('add', 'Silva Forum Topic', ['add', 'Topic'])
    reg.register('add', 'Silva Forum Comment', ['add', 'Comment'])

    # public is done from Five views

    configureAddables(root)
    configureMetadata(root)

def uninstall(root):
    reg = root.service_view_registry
    reg.unregister('edit', 'Silva Forum')
    reg.unregister('edit', 'Silva Forum Topic')
    reg.unregister('edit', 'Silva Forum Comment')
    reg.unregister('add', 'Silva Forum')
    reg.unregister('add', 'Silva Forum Topic')
    reg.unregister('add', 'Silva Forum Comment')

    root.service_views.manage_delObjects(['SilvaForum'])
    root.service_resources.manage_delObjects(['SilvaForum'])

    unconfigureMetadata(root)

def configureAddables(root):
    """Make sure the right items are addable in the root"""
    non_addables = ('Silva Forum Topic',
                    'Silva Forum Comment')
    addables = ('Silva Forum',)
    current_addables = root.get_silva_addables_allowed_in_container()
    new_addables = []
    for a in current_addables:
        if a not in non_addables:
            new_addables.append(a)
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_container(new_addables)

def configureMetadata(context):
    product = package_home(globals())
    schema = os.path.join(product, 'schema')
    collection = context.service_metadata.getCollection()

    for metatypes, setname in (
            (('Silva Forum',), 'silvaforum-forum'),
            (('Silva Forum Topic', 'Silva Forum Comment'), 'silvaforum-item')):
        if setname not in collection.objectIds():
            xmlfile = os.path.join(schema, '%s.xml' % (setname,))
            definition = open(xmlfile, 'r')
            try:
                collection.importSet(definition)
            finally:
                definition.close()
        context.service_metadata.addTypesMapping(
            metatypes, (setname,))
    context.service_metadata.initializeMetadata()

# the following bit has been copied from SilvaLayout, and is a bit
# over-generic, but I guess that's fine...
def unconfigureMetadata(root):
    metadatasets = ['silvaforum-forum', 'silvaforum-item']
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    # Get all content types that have a metadata mapping
    content_types = [item.id for item in mapping.getTypeMappings()]
    tm = []
    # Remove the metadata sets for each content type
    for content_type in content_types:
        chain = mapping.getChainFor(content_type)
        sets = [set.strip() for set in chain.split(',')]
        sets_to_remove = []
        for set in sets:
            if set in metadatasets:
                sets_to_remove.append(set)
        for set in sets_to_remove:
            sets.remove(set)
        map = {'type':content_type,
               'chain':', '.join(sets)}
        tm.append(map)
    mapping.editMappings(default, tm)

    # Remove the metadata set specifications
    collection = root.service_metadata.collection
    for metadataset in metadatasets:
        if collection._getOb(metadataset, None) is not None:
            collection.manage_delObjects(metadataset)

def is_installed(root):
    return hasattr(root.service_views, 'SilvaForum')
