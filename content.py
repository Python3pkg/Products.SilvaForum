# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from five import grok
from zope import component

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.Silva import mangle
from Products.Silva.Content import Content
from Products.Silva.Folder import Folder
from Products.Silva.Publication import Publication
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core.services.interfaces import ICataloging
from silva.translations import translate as _

from Products.SilvaForum.interfaces import IForum, ITopic, IComment


class ForumContainer(object):
    """A container for posts in the forum it used by a forum (contains
    topics) and a topic (contains comments).
    """
    security = ClassSecurityInfo()

    # initialize the regex conditions
    reg_under = re.compile('_+')
    reg_nonword = re.compile('\W')
    reg_start_under = re.compile('^_+')
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
            regex = re.compile('^%s_(\d+)$' % re.escape(id))
            for other_id in self.objectIds():
                match = regex.search(other_id)
                if match:
                    new_int = int(match.group(1))
                    if new_int > highest:
                        highest = new_int
            highest += 1
            id = '%s_%s' % (id, highest)
        return id

    security.declareProtected(
        'Access contents information', 'anonymous_posting_allowed')
    def anonymous_posting_allowed(self):
        metadata = component.getUtility(IMetadataService)
        enabled = metadata.getMetadataValue(
            self, 'silvaforum-forum', 'anonymous_posting')
        return enabled == 'yes'

    security.declareProtected(
        'Access contents information', 'unauthenticated_posting_allowed')
    def unauthenticated_posting_allowed(self):
        metadata = component.getUtility(IMetadataService)
        enabled = metadata.getMetadataValue(
            self, 'silvaforum-forum', 'unauthenticated_posting')
        return enabled == 'yes'

    def is_published(self):
        # always return true to make that the object is always visible
        # in public listings
        return True

    def is_cacheable(self):
        return False

    def get_content(self):
        return self

    def get_content_url(self):
        return self.get_content().absolute_url()

InitializeClass(ForumContainer)


class ForumPost(object):
    """A basic post in the forum (a topic or a comment).
    """
    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(ForumPost, self).__init__(*args, **kwargs)
        self._text = ''

    security.declareProtected('View', 'fulltext')
    def fulltext(self):
        return [self.get_title_or_id(), self.get_text()]

    security.declareProtected('View', 'get_text')
    def get_text(self):
        return self._text

    security.declareProtected('Change Silva content', 'set_text')
    def set_text(self, text):
        self._text = text

    security.declareProtected('Access contents information', 'get_creator')
    def get_creator(self):
        metadata = component.getUtility(IMetadataService)
        anonymous = metadata.getMetadataValue(
            self, 'silvaforum-item', 'anonymous')
        if anonymous == 'yes':
            return _('anonymous')
        return self.sec_get_creator_info().fullname()


InitializeClass(ForumPost)


class Forum(ForumContainer, Publication):
    """A Silva Forum is implements as a web forum, where visitors can
    create topics and comments.
    """
    grok.implements(IForum)
    meta_type = 'Silva Forum'

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(Forum, self).__init__(*args, **kwargs)
        self._lastid = 0
        self.topic_batch_size = 10

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Forum Topic']

    security.declareProtected('View', 'get_topics')
    def get_topics(self):
        """
        return a list of topic objects
        """
        return self.objectValues('Silva Forum Topic')

    security.declareProtected('Change Silva content', 'add_topic')
    def add_topic(self, topic, anonymous=False):
        """ add a topic to the forum
        """
        if anonymous and not self.anonymous_posting_allowed():
            raise ValueError('anonymous posting is not allowed!')
        id = self._generate_id(topic)
        self.manage_addProduct['SilvaForum'].manage_addTopic(id, topic)
        topic = dict(self.objectItems()).get(id)
        if topic is None:
            # apparently zope refused to add the object, probably an id clash.
            # for example (title, or add_topic). topic objects themselves
            # have automaticly generated number parts if needed.
            raise ValueError('Reserved id: "%s"' % id)
        topic.sec_update_last_author_info()
        ICataloging(topic).reindex()
        if anonymous:
            metadata = component.getUtility(IMetadataService)
            binding = metadata.getMetadata(topic)
            binding.setValues('silvaforum-item', {'anonymous': 'yes'})
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
            'creator': obj.get_creator(),
            'commentlen': len(obj.comments()),
        } for obj in self.get_topics()]
        topics.reverse()
        return topics

    security.declareProtected('View', 'number_of_topics')
    def number_of_topics(self):
        return len(self.get_topics())

InitializeClass(Forum)


class Topic(ForumContainer, ForumPost, Folder):
    """Topic of a Silva Forum. It will contains comments posted by users.
    """
    grok.implements(ITopic)
    meta_type = 'Silva Forum Topic'

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        self._lastid = 0
        self.comment_batch_size = 10

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Forum Comment']

    security.declareProtected('Change Silva content', 'add_comment')
    def add_comment(self, title, text, anonymous=False):
        """ add a comment to the topic
        """
        if anonymous and not self.anonymous_posting_allowed():
            raise ValueError('anonymous posting is not allowed!')
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
        comment.sec_update_last_author_info()
        ICataloging(comment).reindex()
        notify_new_comment(comment)
        if anonymous:
            binding = self.get_root().service_metadata.getMetadata(comment)
            binding.setValues('silvaforum-item', {'anonymous': 'yes'})
        return comment

    def comments(self):
        """ returns an iterable of all comments
        """
        return [{
            'id': comment.id,
            'url': comment.absolute_url(),
            'title': comment.get_title(),
            'creator': comment.get_creator(),
            'creation_datetime': comment.get_creation_datetime(),
            'text': comment.get_text(),
            'topic_url': comment.aq_parent.absolute_url(),
        } for comment in self.objectValues('Silva Forum Comment')]

    security.declareProtected('View', 'number_of_comments')
    def number_of_comments(self):
        return len(self.objectValues('Silva Forum Comment'))

InitializeClass(Topic)

class Comment(ForumPost, Content, SimpleItem):
    """A comment is the smallest content of a Silva Forum, contained
    in a topic.
    """
    grok.implements(IComment)
    meta_type = 'Silva Forum Comment'

    def is_published(self):
        return False # always allow removal of this object from the SMI


def notify_new_comment(comment):
    root = comment.get_root()
    service = getattr(root, 'service_subscriptions', None)
    if service is not None:
        service.send_notification(comment, 'forum_event_template')
