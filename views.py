# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from five import grok
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching
from zope import component

from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime

from Products.Silva import mangle

from Products.SilvaForum.emoticons.emoticons import emoticons, \
    smileydata
from Products.SilvaForum.dtformat import dtformat
from Products.SilvaForum.interfaces import IForum, ITopic, \
    IComment, IPostable

from silva.core.interfaces import IEditableMember
from silva.core.views import views as silvaviews
from silva.translations import translate as _

minimal_add_role = 'Authenticated'

grok.templatedir('templates')


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

    def get_smiley_data(self):
        ret = []
        service_url = self.get_resources().emoticons.smilies.absolute_url()
        for image, smileys in smileydata.items():
            ret.append({
                'text': smileys[0],
                'href': service_url + '/' + image,
            })
        return ret

    def get_resources(self):
        return self.context.aq_inner.get_root().service_resources.SilvaForum

    def can_post(self):
        """Return true if the current user is allowed to post.
        """
        sec = getSecurityManager()
        return sec.getUser().has_role(minimal_add_role)

    def authenticate(self):
        if not self.can_post():
            msg = _('Sorry you need to be authorized to use this forum')
            raise Unauthorized(msg)

    def anonymous_posting_allowed(self):
        return self.context.anonymous_posting_allowed()


class UserControls(silvaviews.ContentProvider):
    """Login/User details.
    """

    grok.context(IPostable)
    grok.view(ViewBase)

    def can_edit_profile(self):
        userid = getSecurityManager().getUser().getId()
        # No other nice way to get the member object from here.
        member = self.context.aq_inner.service_members.get_member(
            userid, location=self.context.aq_inner)
        return IEditableMember.providedBy(member)


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
        url = self.context.absolute_url()
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
            comment = self.context.add_comment(
                self.title, self.text, anonymous)
        except ValueError, e:
            self.message = str(e)
            return

        msg = _('Comment added')

        self.response.redirect(
            mangle.urlencode(self.context.absolute_url(), message=msg))


class CommentView(ViewBase):

    grok.context(IComment)

