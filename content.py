# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from five import grok
from zope import schema, component

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import SimpleItem

from Products.Silva import mangle
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.Content import Content
from Products.Silva.Publication import Publication
from Products.Silva.Folder import Folder

from silva.core.conf.interfaces import ITitledContent
from silva.core import conf as silvaconf
from silva.translations import translate as _
from zeam.form import silva as silvaforms

from Products.SilvaForum.interfaces import IForum, ITopic, IComment


class ForumFolderBase(object):
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

    def is_cacheable(self):
        return False

    def get_content(self):
        return self

    def anonymous_posting_allowed(self):
        metadata = component.getUtility(IMetadataService)
        enabled = metadata.getMetadataValue(
            self.get_forum(), 'silvaforum-forum', 'anonymous_posting')
        return enabled == 'yes'

    def unauthenticated_posting_allowed(self):
        metadata = component.getUtility(IMetadataService)
        enabled = metadata.getMetadataValue(
            self.get_forum(), 'silvaforum-forum', 'unauthenticated_posting')
        return enabled == 'yes'


class Forum(ForumFolderBase, Publication):
    """A Silva Forum is rendered as a web forum, where visitors can
    create topics and comments.
    """
    grok.implements(IForum)
    meta_type = 'Silva Forum'
    silvaconf.icon('www/forum.gif')

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(Forum, self).__init__(*args, **kwargs)
        self._lastid = 0
        self.topic_batch_size = 10

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Forum Topic']

    security.declareProtected('View', 'get_forum')
    def get_forum(self):
        return self

    security.declareProtected('View', 'get_topic')
    def get_topic(self, title):
        """
        return a topic object by title
        or none if topic not found
        """
        for topic in self.get_topics():
            if topic.get_title() == title:
                return topic

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
        topic = getattr(self, id, None)
        if topic is None:
            # apparently zope refused to add the object, probably an id clash.
            # for example (title, or add_topic). topic objects themselves
            # have automaticly generated number parts if needed.
            raise ValueError('Reserved id: "%s"' % id)
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

    def is_published(self):
        # always return true to make that the object is always visible
        # in public listings
        return True

InitializeClass(Forum)


class ForumAddForm(silvaforms.SMIAddForm):
    """Forum Add Form
    """
    grok.context(IForum)
    grok.name(u"Silva Forum")


class Topic(ForumFolderBase, Folder):
    """Topic of a Silva Forum. It will contains comments posted by users.
    """
    grok.implements(ITopic)
    silvaconf.icon('www/topic.gif')
    meta_type = 'Silva Forum Topic'

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        self._lastid = 0
        self._text = ''
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
        identifier = self._generate_id(idstring)
        factory = self.manage_addProduct['SilvaForum']
        factory.manage_addComment(identifier, title)
        comment = self[identifier]
        comment.set_text(text)
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

    # XXX this is a bit strange... topic is a Folder type but still has
    # text-data attributes
    security.declareProtected('View', 'get_text')
    def get_text(self):
        return self._text

    security.declareProtected('Change Silva content', 'set_text')
    def set_text(self, text):
        self._text = text

    def is_published(self):
        # always return true to make that the object is always visible
        # in public listings
        return True

    security.declareProtected('Access contents information', 'get_text')
    def get_creator(self):
        metadata = component.getUtility(IMetadataService)
        anonymous = metadata.getMetadataValue(
            self, 'silvaforum-item', 'anonymous')
        if anonymous == 'yes':
            return _('anonymous')
        return self.sec_get_creator_info().fullname()

    security.declareProtected('View', 'number_of_comments')
    def number_of_comments(self):
        return len(self.objectValues('Silva Forum Comment'))

InitializeClass(Topic)


class TopicAddForm(silvaforms.SMIAddForm):
    """Topic Add Form
    """
    grok.context(ITopic)
    grok.name(u'Silva Forum Topic')


class Comment(Content, SimpleItem.SimpleItem):
    """A comment is the smallest content of a Silva Forum, contained
    in a topic.
    """
    grok.implements(IComment)
    silvaconf.icon('www/comment.gif')
    meta_type = 'Silva Forum Comment'

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self._text = ''

    security.declareProtected('View', 'get_text')
    def get_text(self):
        return self._text

    security.declareProtected('Change Silva content', 'set_text')
    def set_text(self, text):
        self._text = text

    security.declareProtected('Access contents information', 'get_text')
    def get_creator(self):
        metadata = component.getUtility(IMetadataService)
        anonymous = metadata.getMetadataValue(
            self, 'silvaforum-item', 'anonymous')
        if anonymous == 'yes':
            return _('anonymous')
        return self.sec_get_creator_info().fullname()

    def is_published(self):
        return False # always allow removal of this object from the SMI

InitializeClass(Comment)


class ICommentSchema(ITitledContent):
    text = schema.Text(
        title=u"comment",
        description=u"Comment text")


class CommentAddForm(silvaforms.SMIAddForm):
    """Comment Add Form.
    """
    grok.context(IComment)
    grok.name(u'Silva Forum Comment')

    fields = silvaforms.Fields(ICommentSchema)


class CommentEditForm(silvaforms.SMIEditForm):
    """Comment Edit Form.
    """
    grok.context(IComment)

    fields = silvaforms.Fields(ICommentSchema).omit('id')
