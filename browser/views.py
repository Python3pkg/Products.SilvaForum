# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime

from Products.Silva import mangle
from Products.SilvaForum.resources.emoticons.emoticons import emoticons, \
    smileydata
from Products.SilvaForum.dtformat import dtformat
from Products.SilvaForum.interfaces import IForum, ITopic, \
    IComment, IPostable

from five import grok
from silva.core.interfaces import ISubscribable
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from zope.i18nmessageid import MessageFactory
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

MINIMAL_ADD_ROLE = 'Authenticated'
_ = MessageFactory('silvaforum')

grok.templatedir('templates')

class ForumResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IPostable, IBrowserRequest)

    def cache_headers(self):
        self.disable_cache()


class ViewBase(silvaviews.View):
    grok.baseclass()

    def format_datetime(self, dt):
        return dtformat(self.request, dt, DateTime())

    def replace_links(self, text):
        # do regex for links and replace at occurrence
        text = re.compile(
            '(((ht|f)tp(s?)\:\/\/|(ht|f)tp(s?)\:'
            '\/\/www\.|www\.|mailto\:)\S+[^).\s])'
        ).sub('<a href="\g<1>">\g<1></a>',text)
        text = re.compile('(<a\shref="www)').sub('<a href="http://www', text)
        return text

    def format_text(self, text):
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8')
        text = mangle.entities(text)
        text = self.replace_links(text)
        text = emoticons(text,
            self.get_resources().emoticons.smilies.absolute_url())
        text = text.replace('\n', '<br />')
        return text

    def get_resources(self):
        return self.context.aq_inner.get_root().service_resources.SilvaForum

def cached_method(method):
    def cached(self):
        key = '_v_cached_method_' + method.func_name
        if key not in self.__dict__:
            self.__dict__[key] = method(self)
        return self.__dict__[key]
    cached.func_name = method.func_name
    return cached


class ContainerViewBase(ViewBase):
    grok.baseclass()

    def update(self):
        super(ContainerViewBase, self).update()
        user = getSecurityManager().getUser()

        self.captcha_posting = self.context.unauthenticated_posting_allowed()
        self.anonymous_posting = self.context.anonymous_posting_allowed()
        self.is_logged_in = user.has_role(MINIMAL_ADD_ROLE)
        self.need_captcha = self.captcha_posting and not self.is_logged_in
        self.need_anonymous_option = (
            self.anonymous_posting and not self.need_captcha)
        self.can_post = self.captcha_posting or self.is_logged_in
        self.have_subscriptions = False
        service = self.context.aq_inner.service_subscriptions
        manager = ISubscribable(self.context.aq_inner, None)
        if service is not None:
            self.have_subscriptions = (
                service.subscriptionsEnabled() and
                manager is not None and
                manager.isSubscribable())
        self.inline_subscription = False
        if self.have_subscriptions:
            email = self.get_user_email()
            if email:
                if not manager.isSubscribed(email):
                    self.inline_subscription = True

        self.messages = []

    def get_smiley_data(self):
        ret = []
        service_url = self.get_resources().emoticons.smilies.absolute_url()
        for image, smileys in smileydata.items():
            ret.append({
                'text': smileys[0],
                'href': service_url + '/' + image,
            })
        return ret

    def authenticate(self):
        if not self.is_logged_in:
            msg = _('Sorry, you need to be authenticated to use this forum.')
            raise Unauthorized(msg)
        return True

    @cached_method
    def get_member(self):
        userid = getSecurityManager().getUser().getId()
        return self.context.aq_inner.service_members.get_member(userid)

    def get_preview_username(self, anonymous):
        if anonymous or self.need_captcha:
            return _('anonymous')
        else:
            member = self.get_member()
            if member is None:
                return _('anonymous')
            return member.fullname()

    @cached_method
    def get_user_email(self):
        member = self.get_member()
        if member is not None:
            return member.email()
        return None

    def authorized_to_post(self):
        # This is intended for the posting action, not the template.
        if self.need_captcha:
            value = self.request.form.get('captcha')
            captcha = getMultiAdapter(
                (self.context, self.request), name='captcha')
            if not captcha.verify(value):
                self.messages = [_(u'Invalid captcha value.')]
                return False
            return True
        return self.authenticate()

    def do_subscribe_user(self, content):
        if self.inline_subscription:
            if self.request.form.get('subscribe', False):
                service = self.context.aq_inner.service_subscriptions
                try:
                    service.requestSubscription(
                        content, self.get_user_email())
                except:
                    return _(u"An error happened while subscribing "
                             u"you to the post.")
                return _(u"A confirmation mail have been sent "
                         u"for your subscription.")
        return None

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
    subscribe = True

    def action_preview(self, topic, anonymous):
        self.topic = topic
        self.anonymous = anonymous
        self.username = self.get_preview_username(anonymous)
        self.preview = True
        self.preview_validated = bool(topic)
        self.topic_missing = not topic
        self.subscribe = 'subscribe' in self.request.form

    def action_post(self, topic, anonymous):
        success = False
        if self.authorized_to_post():
            if not topic:
                self.topic_missing = True
            else:
                try:
                    content = self.context.aq_inner.add_topic(
                        topic, self.need_captcha or anonymous)
                except ValueError, e:
                    self.messages = [str(e)]
                else:
                    self.messages = [_('Topic added.')]
                    message = self.do_subscribe_user(content)
                    if message:
                        self.messages.append(message)
                    success = True
        if not success:
            self.topic = topic
            self.anonymous = anonymous
            self.subscribe = 'subscribe' in self.request.form

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
            self.context.aq_inner.topics(), count=self.context.topic_batch_size,
            name='topics', request=self.request)

        # We don't want batch links to include form data.
        navigation = getMultiAdapter(
            (self.context, self.topics, self.request), IBatching)
        navigation.keep_form_data = False
        self.navigation = navigation()


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
    subscribe = True

    def get_forum(self):
        return self.context.aq_inner.aq_parent

    def get_topic_title(self):
        return self.context.get_title()

    def action_preview(self, title, text, anonymous):
        self.title = title
        if not title:
            self.title = self.get_topic_title()
        self.text = text
        self.anonymous = anonymous
        self.username = self.get_preview_username(anonymous)
        self.preview = True
        self.preview_validated = bool(text)
        self.text_missing = not text
        self.subscribe = 'subscribe' in self.request.form

    def action_post(self, title, text, anonymous):
        success = False
        if self.authorized_to_post():
            if not title:
                title = self.get_topic_title()
            if not text:
                self.text_missing = True
            else:
                try:
                    self.context.aq_inner.add_comment(
                        title, text, self.need_captcha or anonymous)
                except ValueError, e:
                    self.messages = [str(e)]
                else:
                    self.messages = [_('Comment added.')]
                    success = True
                    message = self.do_subscribe_user(self.context.aq_inner)
                    if message:
                        self.messages.append(message)

        if not success:
            self.title = title
            self.text = text
            self.anonymous = anonymous
            self.subscribe = 'subscribe' in self.request.form

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
            self.context.aq_inner.comments(), count=self.context.comment_batch_size,
            name='comments', request=self.request)

        # We don't want batch links to include form data.
        navigation = getMultiAdapter(
            (self.context, self.comments, self.request), IBatching)
        navigation.keep_form_data = False
        self.navigation = navigation()
        self.action_url = navigation.last + '#forum-bottom'


class CommentView(ViewBase):
    """View a comment.
    """
    grok.context(IComment)
