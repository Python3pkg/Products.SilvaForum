# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from five import grok
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope import component
from zope.cachedescriptors.property import CachedProperty

from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime

from Products.Silva import mangle

from Products.SilvaForum.emoticons import emoticons, smileydata
from Products.SilvaForum.dtformat import dtformat
from Products.SilvaForum.interfaces import IForum, ITopic, \
    IComment, IPostable

from silva.core.views import views as silvaviews
from silva.translations import translate as _

MINIMAL_ADD_ROLE = 'Authenticated'

grok.templatedir('templates')

LINK_RE = re.compile(
    r'(((ht|f)tp(s?)\:\/\/|(ht|f)tp(s?)\:'
    r'\/\/www\.|www\.|mailto\:)\S+[^).\s])')
ABSOLUTE_LINK_RE = re.compile(r'(<a\shref="www)')

def replace_links(text):
    # do regex for links and replace at occurrence
    text = LINK_RE.sub('<a href="\g<1>">\g<1></a>', text)
    return ABSOLUTE_LINK_RE.sub('<a href="http://www', text)


class ViewBase(silvaviews.View):

    grok.baseclass()

    def format_datetime(self, dt):
        return dtformat(self.request, dt, DateTime())

    def format_text(self, text):
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8')
        text = emoticons(
            replace_links(
                mangle.entities(text)), self.emoticons_directory)
        return text.replace('\n', '<br />')

    @CachedProperty
    def emoticons_directory(self):
        return self.static['emoticons']()

    def smileys(self):
        smileys = []
        for filename, syntaxes in smileydata.items():
            smileys.append({
                'text': syntaxes[0],
                'href': '/'.join((self.emoticons_directory, filename)),
                })
        return smileys

    def can_post(self):
        """Return true if the current user is allowed to post.
        """
        sec = getSecurityManager()
        return sec.getUser().has_role(MINIMAL_ADD_ROLE)

    def authenticate(self):
        if not self.can_post():
            msg = _('Sorry you need to be authorized to use this forum')
            raise Unauthorized(msg)

    @CachedProperty
    def unauthenticated_posting_allowed(self):
        pass

    @CachedProperty
    def anonymous_posting_allowed(self):
        return self.context.anonymous_posting_allowed()


class UserControls(silvaviews.ContentProvider):
    """Login/User details.
    """
    grok.context(IPostable)
    grok.view(ViewBase)


class ForumView(ViewBase):
    """View for a forum.
    """
    grok.context(IForum)

    def update(self, authenticate=False, anonymous=False,
               preview=False, cancel=False, topic=None, message=''):
        if authenticate:
            self.authenticate()

        self.topics = batch(
            self.context.topics(), count=self.context.topic_batch_size,
            name='topics', request=self.request)

        self.batch = component.getMultiAdapter(
            (self.context, self.topics, self.request),
            IBatching)()

        self.topic = unicode(topic or '', 'utf-8').strip()
        self.message = unicode(message, 'utf-8')
        self.anonymous = anonymous
        self.preview = preview
        self.preview_topic = preview and self.topic
        self.preview_not_topic = preview and not self.topic

        if (preview or cancel or topic is None):
            return

        self.authenticate()

        if not self.topic:
            self.message = _('Please provide a subject')
            return

        try:
            self.context.add_topic(self.topic, anonymous)
        except ValueError, e:
            self.message = str(e)
            return
        msg = _('Topic added')
        self.response.redirect(
            mangle.urlencode(self.context.absolute_url(), message=msg))


class TopicView(ViewBase):
    """ View on a Topic. The TopicView is a collection of comments.
    """
    grok.context(ITopic)

    def update(self, authenticate=False, anonymous=False, preview=False,
               cancel=False, title=None, text=None, message=''):
        if authenticate:
            self.authenticate()

        self.comments = batch(
            self.context.comments(), count=self.context.comment_batch_size,
            name='comments', request=self.request)

        self.batch = component.getMultiAdapter(
            (self.context, self.comments, self.request),
            IBatching)()

        self.title = unicode(title or '', 'UTF-8').strip()
        self.text = unicode(text or '', 'UTF-8').strip()
        self.message = unicode(message, 'utf-8')
        self.anonymous = anonymous
        self.preview = preview
        self.preview_title_text = preview and self.title and self.text
        self.preview_not_title = preview and not self.title
        self.preview_not_text = preview and not self.text

        if (preview or cancel or (text is None and title is None)):
            return

        self.authenticate()

        if not title and not text:
            self.message = _('Please provide a title and a text')
            return

        try:
            self.context.add_comment(self.title, self.text, anonymous)
        except ValueError, e:
            self.message = str(e)
            return

        msg = _('Comment added')

        self.response.redirect(
            mangle.urlencode(self.context.absolute_url(), message=msg))


class CommentView(ViewBase):
    """View a comment.
    """
    grok.context(IComment)
