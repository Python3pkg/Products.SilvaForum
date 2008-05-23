# Copyright (c) 2007 Infrae. All rights reserved.
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
from interfaces import IForum, ITopic, IComment

class FiveViewable(object):
    """ A Comment is added to a Topic of a Forum. Usually it's added via a
        public interface, as opposed to the Silva Management Interface. 
        Comments are not versioned, and can be edited or deleted as needed for
        moderation of the Forum.  
    """

    # mixin to override .view()instead of using the view registry view() 
    # uses Five

    def view(self):
        """ render the public Five view for this object
        """
        # if a parameter ?include is in the request, call the original view,
        # and use it as input for the include view. When using ?include we expect
        # that '/view' was added to the url, and it will return a page suitable
        # for including in other documents
        # XXX maybe we should use an adapter here?
        result = getMultiAdapter((self, self.REQUEST), name=u'view.html')()
        if self.REQUEST.form.has_key('include'):
            view = getMultiAdapter((self, self.REQUEST), name=u'include.html')
            result = view(content=result)
        return result

    preview = view

class ForumFolderBase(FiveViewable):
    """ A Forum can be added to your site to facilitate discussions. A Forum is
        divided into Topics, which in turn have Comments. Users who wish to 
        post to the Forum must be authenticated. A login box will appear if a
        post is attempted from a public page by an unauthenticated user. 
        Comments can be moderated in the Silva Management Interface (SMI). 
    """

    # Make topic or text string and id chop on character 20

    # initialize the regex conditions
    reg_under = re.compile('_+')
    reg_nonword = re.compile('\W')
    reg_start_under = re.compile('^_+')
    reg_number_at_end = re.compile('\d+$')
    def _generate_id(self, string):
        """ This produces a chopped string id from a title, or
            text, or else uses unknown. For dublicates the
            method adds 1.
        """
        string = string.strip()
        if len(string) > 20:
            string = string[:20]
        id = str(mangle.Id(self, string).cook())
        # regex the cooked id and strip invalid characters
        # replace multiple underscores with single underscores
        # if no string use 'unknown'
        id = self.reg_start_under.sub('',
                self.reg_under.sub('_',
                    self.reg_nonword.sub('_', id)))
        if not id:
            id = 'unknown'
        if id in self.objectIds():
            highest = 1
            for other_id in self.objectIds():
                match =self.reg_number_at_end.search(other_id)
                if other_id.startswith(id) and match:
                    highest = int(match.group(0))
            highest += 1
            id = '%s_%s' % (id, highest)
        return id

class Forum(ForumFolderBase, Publication):
    interface.implements(IForum)
    meta_type = 'Silva Forum'

    _addables_allowed_in_publication = ('Silva Forum Topic',)

    def __init__(self, *args, **kwargs):
        super(Forum, self).__init__(*args, **kwargs)
        self._lastid = 0
        self.topic_batch_size = 10

    def get_topic(self, title):
        """
        return a topic object by title
        or none if topic not found
        """
        for topic in self.get_topics():
            if topic.get_title() == title:
                return topic

    def get_topics(self):
        """
        return a list of topic objects
        """
        return self.objectValues('Silva Forum Topic')
        
    
    def add_topic(self, topic):
        """ add a topic to the forum
        """
        
        id = self._generate_id(topic)
        self.manage_addProduct['SilvaForum'].manage_addTopic(id, topic)
        topic = dict(self.objectItems()).get(id)
        if topic is None:
            # apparently zope refused to add the object, probably an id clash.
            # for example (title, or add_topic). topic objects themselves 
            # have automaticly generated number parts if needed.
            raise ValueError('Reserved id: "%s"' % id)
        return topic

    def topics(self):
        """ returns an iterable of all topics (topics)
        """
        # XXX Why not return a list of topic objects?

        # XXX note that this mostly exists because we intend to add more
        # functionality (e.g. searching, ordering) later
        topics = [{
            'url': obj.absolute_url(),
            'title': obj.get_title(),
            'creation_datetime': obj.get_creation_datetime(),
            'creator': obj.sec_get_creator_info().fullname(),
            'commentlen': len(obj.comments()),
        } for obj in self.get_topics()]
        topics.reverse()
        return topics

    def number_of_topics(self):
        return len(self.get_topics())

    def is_published(self):
        # always return true to make that the object is always visible in public
        # listings
        return True

class Topic(ForumFolderBase, Folder):
    interface.implements(ITopic)
    meta_type = 'Silva Forum Topic'

    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        self._lastid = 0
        self._text = ''
        self.comment_batch_size = 10

    def add_comment(self, title, text):
        """ add a comment to the topic
        """
        idstring = title
        if not idstring:
            idstring = text
        id = self._generate_id(idstring)
        self.manage_addProduct['SilvaForum'].manage_addComment(id, title)
        comment = dict(self.objectItems()).get(id)
        if comment is None:
            # see add_topic comments
            raise ValueError('Reserved id: "%s"' % id)
        comment.set_text(text)
        return comment
    
    def comments(self):
        """ returns an iterable of all comments
        """
        comments = [{
            'id': obj.id,
            'url': obj.absolute_url(),
            'title': obj.get_title(),
            'creator': obj.sec_get_creator_info().fullname(),
            'creation_datetime': obj.get_creation_datetime(),
            'text': obj.get_text(),
            'topic_url': obj.aq_parent.absolute_url(),
        } for obj in self.objectValues('Silva Forum Comment')]
        comments
        return comments

    # XXX this is a bit strange... topic is a Folder type but still has
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
    
    def number_of_comments(self):
        return len(self.objectValues('Silva Forum Comment'))

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

