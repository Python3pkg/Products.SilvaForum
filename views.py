# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime

from Products.Silva import mangle
from Products.SilvaForum.emoticons import emoticons, smileydata
from Products.SilvaForum.dtformat import dtformat
from Products.SilvaForum.interfaces import IForum, ITopic, \
    IComment, IPostable

from five import grok
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.translations import translate as _
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest

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


class FindResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, IPostable)

    def cache_headers(self):
        self.disable_cache()


class ViewBase(silvaviews.View):
    grok.baseclass()

    def update(self):
        self.emoticons_directory = self.static['emoticons']()

    def format_datetime(self, dt):
        return dtformat(self.request, dt, DateTime())

    def format_text(self, text):
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8')
        text = emoticons(
            replace_links(
                mangle.entities(text)), self.emoticons_directory)
        return text.replace('\n', '<br />')


class ContainerViewBase(ViewBase):
    grok.baseclass()

    def update(self):
        super(ContainerViewBase, self).update()
        self.captcha_posting = self.context.unauthenticated_posting_allowed()
        self.anonymous_posting = self.context.anonymous_posting_allowed()
        sm = getSecurityManager()
        self.is_logged_in = sm.getUser().has_role(MINIMAL_ADD_ROLE)

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
        if self.captcha_posting:
            return True
        return self.is_logged_in

    def authenticate(self):
        if not self.is_logged_in:
            msg = _('Sorry you need to be authorized to use this forum')
            raise Unauthorized(msg)



class UserControls(silvaviews.ContentProvider):
    """Login/User details.
    """
    grok.context(IPostable)
    grok.view(ContainerViewBase)


class ForumView(ContainerViewBase):
    """View for a forum.
    """
    grok.context(IForum)

    def update(self, authenticate=False, anonymous=False,
               preview=False, cancel=False, topic=None, message=''):
        super(ForumView, self).update()
        if authenticate:
            self.authenticate()

        self.topic = unicode(topic or '', 'utf-8').strip()
        self.message = unicode(message, 'utf-8')
        self.anonymous = anonymous
        self.preview = preview
        self.preview_topic = preview and self.topic
        self.preview_not_topic = preview and not self.topic

        if not (preview or cancel or topic is None):
            self.authenticate()

            if not self.topic:
                self.message = _('Please provide a subject')
            else:
                try:
                    self.context.add_topic(self.topic, anonymous)
                except ValueError, e:
                    self.message = str(e)
                else:
                    self.message = _('Topic added')
                    self.topic = u''

        self.topics = batch(
            self.context.topics(), count=self.context.topic_batch_size,
            name='topics', request=self.request)

        self.batch = component.getMultiAdapter(
            (self.context, self.topics, self.request),
            IBatching)()


class TopicView(ContainerViewBase):
    """ View on a Topic. The TopicView is a collection of comments.
    """
    grok.context(ITopic)

    def update(self, authenticate=False, anonymous=False, preview=False,
               cancel=False, title=None, text=None, message=''):
        super(TopicView, self).update()
        if authenticate:
            self.authenticate()

        self.title = unicode(title or '', 'UTF-8').strip()
        self.text = unicode(text or '', 'UTF-8').strip()
        self.message = unicode(message, 'utf-8')
        self.anonymous = anonymous
        self.preview = preview
        self.preview_title_text = preview and self.title and self.text
        self.preview_not_title = preview and not self.title
        self.preview_not_text = preview and not self.text

        if not (preview or cancel or (text is None and title is None)):
            self.authenticate()

            if not title and not text:
                self.message = _('Please provide a title and a text')
            else:
                try:
                    self.context.add_comment(self.title, self.text, anonymous)
                except ValueError, e:
                    self.message = str(e)
                else:
                    self.message = _('Comment added')

        self.comments = batch(
            self.context.comments(), count=self.context.comment_batch_size,
            name='comments', request=self.request)

        self.batch = component.getMultiAdapter(
            (self.context, self.comments, self.request),
            IBatching)()


class CommentView(ViewBase):
    """View a comment.
    """
    grok.context(IComment)
