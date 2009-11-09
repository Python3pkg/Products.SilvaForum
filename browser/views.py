# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import re

from AccessControl import getSecurityManager, Unauthorized

from Products.Silva import mangle
from silva.core.interfaces import IEditableMember

from Products.SilvaForum.resources.emoticons.emoticons import emoticons, \
    smileydata
from Products.SilvaForum.dtformat.dtformat import format_dt

from DateTime import DateTime
from urllib import quote

from Products.SilvaForum.i18n import translate as _
from Products.SilvaForum.interfaces import IForum, ITopic, \
    IComment, IPostable

from silva.core.views import views as silvaviews
from five import grok

minimal_add_role = 'Authenticated'

grok.templatedir('templates')


class ViewBase(silvaviews.View):

    grok.baseclass()

    def format_datetime(self, dt):
        return format_dt(self, dt, DateTime())

    def render_url(self, url, **qs_params):
        if not qs_params:
            return url

        # add /view to url if in include mode, also make sure
        # the ?include parameter is present
        if self.request.has_key('include'):
            qs_params['include'] = self.request['include']
            if not url.endswith('/view'):
                url += '/view'

        params = []
        for key, val in qs_params.items():
            params.append('%s=%s' %  (key, quote(unicode(val).encode('utf8'))))

        return '%s?%s' % (url, '&'.join(params))

    def get_batch_first_link(self, current_offset):
        if current_offset == 0:
            return
        return self.render_url(self.context.absolute_url(), batch_start=0)

    def get_batch_prev_link(self, current_offset, batchsize=10):
        if current_offset < batchsize:
            return
        prevoffset = current_offset - batchsize
        return self.render_url(
            self.context.absolute_url(), batch_start=prevoffset)

    def get_batch_next_link(self, current_offset, numitems, batchsize=10):
        if current_offset >= (numitems - batchsize):
            return
        offset = current_offset + batchsize
        return self.render_url(self.context.absolute_url(), batch_start=offset)

    def get_last_batch_start(self, numitems, batchsize=10):
        rest = numitems % batchsize
        offset = numitems - rest
        if rest == 0:
            offset -= batchsize
        return offset

    def get_batch_last_link(self, current_offset, numitems, batchsize=10):
        if current_offset >= (numitems - batchsize):
            return
        offset = self.get_last_batch_start(numitems)
        return self.render_url(self.context.absolute_url(), batch_start=offset)

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
        root = self.context.aq_inner.get_root()
        text = self.replace_links(text)
        text = emoticons(text,
            self.get_resources().emoticons.smilies.absolute_url())
        text = text.replace('\n', '<br />')
        return text

    def get_smiley_data(self):
        ret = []
        root = self.context.aq_inner.get_root()
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
            '%s?message=%s' % (
                self.context.absolute_url(),
                quote(msg)))


class TopicView(ViewBase):
    """ View on a Topic. The TopicView is a collection of comments.
    """

    grok.context(ITopic)

    def update(self, authenticate=False, anonymous=False, preview=False,
               cancel=False, title=None, text=None, message=''):
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
        num_items = self.context.number_of_comments()

        url = self.render_url(self.context.absolute_url(),
                              message=msg,
                              batch_start=self.get_last_batch_start(num_items))

        self.response.redirect('%s#bottom' % url)


class CommentView(ViewBase):

    grok.context(IComment)

