from zope import interface
from zope.component import getMultiAdapter
from OFS import SimpleItem

from Products.Silva.Content import Content
from Products.Silva.Publication import Publication
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.Folder import Folder
from Products.Silva.i18n import translate as _

from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

class IForum(interface.Interface):
    pass

class IThread(interface.Interface):
    pass

class IComment(interface.Interface):
    pass

class FiveViewable:
    """ mixin to override .view()

        instead of using the view registry view() uses Five
    """
    def view(self):
        """ render the public Five view for this object
        """
        content = self.get_viewable()
        view = getMultiAdapter((self, self.REQUEST), name=u'index.html')
        # XXX hrmph, had some strange context issues here ('view' would be
        # unwrapped in the template), but for some reason this seems to work
        # without a problem now... perhaps because of changes in
        # configure.zcml?!?
        return view()

    preview = view

class Forum(FiveViewable, Publication):
    interface.implements(IForum)
    meta_type = 'Silva Forum'

    _addables_allowed_in_publication = ('Silva Forum Thread',)

    def __init__(self, *args, **kwargs):
        super(Forum, self).__init__(*args, **kwargs)
        self._lastid = 0
    
    def add_thread(self, topic, text):
        """ add a thread to the forum
        """
        id = _generate_id(self)
        self.manage_addProduct['SilvaForum'].manage_addThread(id, topic)
        thread = getattr(self, id)
        thread.set_text(text)
        return thread

    def threads(self):
        """ returns an iterable of all threads (topics)
        """
        # XXX note that this mostly exists because we intend to add more
        # functionality (e.g. searching, ordering) later
        ret = []
        for obj in self.objectValues('Silva Forum Thread'):
            ret.append(obj)
        return ret

class Thread(FiveViewable, Folder):
    interface.implements(IThread)
    meta_type = 'Silva Forum Thread'

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self._lastid = 0
        self._text = ''

    def add_comment(self, title, text):
        """ add a comment to the thread
        """
        id = _generate_id(self)
        self.manage_addProduct['SilvaForum'].manage_addComment(id, title)
        comment = getattr(self, id)
        comment.set_text(text)
        return comment
    
    def comments(self):
        """ returns an iterable of all comments
        """
        ret = []
        for obj in self.objectValues('Silva Forum Comment'):
            ret.append(obj)
        return ret

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def get_silva_addables_allowed(self):
        return ('Silva Forum Comment',)

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

    def is_published(self):
        return False # always allow removal of this object from the SMI

def _generate_id(obj):
    # XXX not very nice, and also not thread-safe...
    while 1:
        obj._lastid += 1
        if hasattr(obj, str(obj._lastid)):
            continue
        return str(obj._lastid)

