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
from silva.core.services.interfaces import IMemberService
from silva.translations import translate as _
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope.component import getMultiAdapter, getUtility
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
        user = getSecurityManager().getUser()

        self.captcha_posting = self.context.unauthenticated_posting_allowed()
        self.anonymous_posting = self.context.anonymous_posting_allowed()
        self.is_logged_in = user.has_role(MINIMAL_ADD_ROLE)
        self.need_captcha = self.captcha_posting and not self.is_logged_in
        self.need_anonymous_option = self.anonymous_posting and not self.need_captcha
        self.can_post = self.captcha_posting or self.is_logged_in

        self.message = u''

    def smileys(self):
        smileys = []
        for filename, syntaxes in smileydata.items():
            smileys.append({
                'text': syntaxes[0],
                'href': '/'.join((self.emoticons_directory, filename)),
                })
        return smileys

    def authenticate(self):
        if not self.is_logged_in:
            msg = _('Sorry, you need to be authenticated to use this forum.')
            raise Unauthorized(msg)
        return True

    def get_preview_username(self, anonymous):
        if anonymous or self.need_captcha:
            return _('anonymous')
        else:
            userid = getSecurityManager().getUser().getId()
            member = getUtility(IMemberService).get_member(userid)
            if member is None:
                return _('anonymous')
            return member.fullname()

    def authorized_to_post(self):
        # This is intended for the posting action, not the template.
        if self.need_captcha:
            value = self.request.form.get('captcha')
            captcha = getMultiAdapter(
                (self.context, self.request), name='captcha')
            if not captcha.verify(value):
                self.message = _(u'Invalid captcha value')
                return False
            return True
        return self.authenticate()

    def action_authenticate(self, *args):
        self.authenticate()

    ACTIONS = [
        ('action.authenticate', action_authenticate),
        ('action.clear', lambda *args: None,),
        ]


class UserControls(silvaviews.ContentProvider):
    """Login/User details.
    """
    grok.context(IPostable)
    grok.view(ContainerViewBase)


class ForumView(ContainerViewBase):
    """View for a forum.
    """
    grok.context(IForum)

    topic = ''
    topic_missing = False
    username = ''
    anonymous = False
    preview = False
    preview_validated = False

    def action_preview(self, topic, anonymous):
        self.topic = topic
        self.anonymous = anonymous
        self.username = self.get_preview_username(anonymous)
        self.preview = True
        self.preview_validated = bool(topic)
        self.topic_missing = not topic

    def action_post(self, topic, anonymous):
        success = False
        if self.authorized_to_post():
            if not topic:
                self.topic_missing = True
            else:
                try:
                    self.context.add_topic(
                        topic, self.need_captcha or anonymous)
                except ValueError, e:
                    self.message = str(e)
                else:
                    self.message = _('Topic added.')
                    success = True
        if not success:
            self.topic = topic
            self.anonymous = anonymous

    ACTIONS = ContainerViewBase.ACTIONS + [
        ('action.preview', action_preview),
        ('action.post', action_post),
        ]

    def update(self, topic=None, anonymous=False):
        super(ForumView, self).update()

        topic = unicode(topic or '', 'UTF-8').strip()

        for name, action in self.ACTIONS:
            if name in self.request.form:
                action(self, topic, anonymous)
                break

        self.topics = batch(
            self.context.topics(), count=self.context.topic_batch_size,
            name='topics', request=self.request)

        # We don't want batch links to include form data.
        self.request.form.clear()
        self.navigation = getMultiAdapter(
            (self.context, self.topics, self.request), IBatching)()


class TopicView(ContainerViewBase):
    """ View on a Topic. The TopicView is a collection of comments.
    """
    grok.context(ITopic)

    title = ''
    text = ''
    text_missing = False
    username = ''
    anonymous = False
    preview = False
    preview_validated = False

    def get_topic_title(self):
        return self.context.get_title()

    def action_preview(self, title, text, anonymous):
        self.title = title if title else self.get_topic_title()
        self.text = text
        self.anonymous = anonymous
        self.username = self.get_preview_username(anonymous)
        self.preview = True
        self.preview_validated = bool(text)
        self.text_missing = not text

    def action_post(self, title, text, anonymous):
        success = False
        if self.authorized_to_post():
            if not title:
                title = self.get_topic_title()
            if not text:
                self.text_missing = True
            else:
                try:
                    self.context.add_comment(
                        title, text, self.need_captcha or anonymous)
                except ValueError, e:
                    self.message = str(e)
                else:
                    self.message = _('Comment added.')
                    success = True
        if not success:
            self.title = title
            self.text = text
            self.anonymous = anonymous

    ACTIONS = ContainerViewBase.ACTIONS + [
        ('action.preview', action_preview),
        ('action.post', action_post),
        ]

    def update(self, title=None, text=None, anonymous=False):
        super(TopicView, self).update()

        title = unicode(title or '', 'UTF-8').strip()
        text = unicode(text or '', 'UTF-8').strip()

        for name, action in self.ACTIONS:
            if name in self.request.form:
                action(self, title, text, anonymous)
                break

        self.comments = batch(
            self.context.comments(), count=self.context.comment_batch_size,
            name='comments', request=self.request)

        # We don't want batch links to include form data.
        self.request.form.clear()
        navigation = getMultiAdapter(
            (self.context, self.comments, self.request), IBatching)
        self.navigation = navigation()
        self.action_url = navigation.last + '#forum-bottom'


class CommentView(ViewBase):
    """View a comment.
    """
    grok.context(IComment)
