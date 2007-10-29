# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

import re
from zope import interface
from zope.component import getMultiAdapter
from OFS import SimpleItem

from Products.Silva import mangle
from Products.Silva.Content import Content
from Products.Silva.Publication import Publication
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.Folder import Folder
from Products.Silva.i18n import translate as _

from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from interfaces import IForum, IThread, IComment

class FiveViewable(object):
    """ mixin to override .view()
        instead of using the view registry view() uses Five
    """
    def view(self):
        """ render the public Five view for this object
        """
        view = getMultiAdapter((self, self.REQUEST), name=u'index.html')
        # XXX hrmph, had some strange context issues here ('view' would be
        # unwrapped in the template), but for some reason this seems to work
        # without a problem now... perhaps because of changes in
        # configure.zcml?!?
        return view()

    preview = view

class ForumFolderBase(FiveViewable):
    """ Make topic or text string and id chop on character 20
    """
    reg_under = re.compile('_+')
    reg_nonword = re.compile('\W')
    reg_start_under = re.compile('^_+')
    def _generate_id(self, string):
        if len(string) > 20:
            string = string[:20]
        id = str(mangle.Id(self, string).cook())
        # regex the cooked id and strip invalid characters
        # replace multiple underscores with single underscores
        #reg1 = re.compile('_')
        #reg2 = re.compile('\W')
        #id = self.reg1.sub('_', self.reg2.sub('_', id))
        #id = self.reg1.sub('_', self.reg2.sub('_', input))
        id = self.reg_start_under.sub('',
                self.reg_under.sub('_',
                    self.reg_nonword.sub('_', id)))
        if not id:
            id = 'unknown'
        if id in self.objectIds():
            highest = 1
            for other_id in self.objectIds():
                if other_id.startswith(id) and '__' in other_id:
                    numpart = other_id.split('__')[-1]
                    if numpart.isdigit():
                        highest = int(numpart)
            highest += 1
            id = '%s__%s' % (id, highest)
        return id
    

class Forum(ForumFolderBase, Publication):
    interface.implements(IForum)
    meta_type = 'Silva Forum'

    _addables_allowed_in_publication = ('Silva Forum Thread',)

    def __init__(self, *args, **kwargs):
        super(Forum, self).__init__(*args, **kwargs)
        self._lastid = 0
    
    def add_thread(self, topic, text):
        """ add a thread to the forum
        """
        id = self._generate_id(topic)
        self.manage_addProduct['SilvaForum'].manage_addThread(id, topic)
        thread = dict(self.objectItems()).get(id)
        if thread is None:
            # apparently zope refused to add the object, probably an id clash.
            # for example (title, or add_thread). Thread objects themselves 
            # have automaticly generated number parts if needed.
            raise ValueError('Reserved id: "%s"' % id)
        thread.set_text(text)
        return thread

    def threads(self):
        """ returns an iterable of all threads (topics)
        """
        # XXX Why not return a list of thread objects?

        # XXX note that this mostly exists because we intend to add more
        # functionality (e.g. searching, ordering) later
        threads = [{
            'url': obj.absolute_url(),
            'title': obj.get_title(),
            'creation_datetime': obj.get_creation_datetime(),
            'creator': obj.sec_get_creator_info().fullname(),
            'commentlen': len(obj.comments()),
        } for obj in self.objectValues('Silva Forum Thread')]
        threads
        return threads

    def is_published(self):
        # always return true to make that the object is always visible in public
        # listings
        return True

class Thread(ForumFolderBase, Folder):
    interface.implements(IThread)
    meta_type = 'Silva Forum Thread'

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self._lastid = 0
        self._text = ''
    
    def add_comment(self, title, text):
        """ add a comment to the thread
        """
        idstring = title
        if not idstring:
            idstring = text
        id = self._generate_id(idstring)
        self.manage_addProduct['SilvaForum'].manage_addComment(id, title)
        comment = dict(self.objectItems()).get(id)
        if comment is None:
            # see add_thread comments
            raise ValueError('Reserved id: "%s"' % id)
        comment.set_text(text)
        return comment
    
    def comments(self):
        """ returns an iterable of all comments
        """
        comments = [{
            'url': obj.absolute_url(),
            'title': obj.get_title(),
            'creator': obj.sec_get_creator_info().fullname(),
            'creation_datetime': obj.get_creation_datetime(),
            'text': obj.get_text(),
        } for obj in self.objectValues('Silva Forum Comment')]
        comments
        return comments

    # XXX this is a bit strange... Thread is a Folder type but still has
    # text-data attributes
    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def get_silva_addables_allowed(self):
        return ('Silva Forum Comment',)

    def is_published(self):
        # always return true to make that the object is always visible in public
        # listings
        return True

class Comment(FiveViewable, CatalogPathAware, Content, SimpleItem.SimpleItem):
    interface.implements(IComment)
    meta_type = 'Silva Forum Comment'
    default_catalog = 'service_catalog'

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self._text = ''

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text
        self = self._get_self()
        self.sec_update_last_author_info()

    def _get_self(self):
        # XXX hack to work around strange problem with Five: for some reason
        # the acquisition path seems to be broken when traversing from a Five
        # view: it ends up on a 'Products.Five.metaclass.SimpleViewClass'
        # instead of the expected app root
        pp = self.getPhysicalPath()
        sroot = self.get_root()
        return sroot.restrictedTraverse(pp)

    def is_published(self):
        return False # always allow removal of this object from the SMI

