import re

from Products.Five import BrowserView
from Products.Silva.browser.headers import Headers
from Products.Silva import mangle
from Products.Silva import SilvaPermissions
from Products.SilvaForum.resources.emoticons.emoticons import emoticons, smileydata, get_alt_name
from Products.SilvaForum.dtformat.dtformat import format_dt
from DateTime import DateTime
from AccessControl import getSecurityManager, Unauthorized

from urllib import quote

minimal_add_role = 'Authenticated'

class ViewBase(Headers):
    def format_datetime(self, dt):
        return format_dt(dt, DateTime())
    
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
        return self.render_url(self.context.absolute_url(), batch_start=prevoffset)

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
        text = re.compile('(((ht|f)tp(s?)\:\/\/|(ht|f)tp(s?)\:\/\/www\.|www\.|mailto\:)\S+)').sub('<a href="\g<1>">\g<1></a>',text)
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

class ForumView(ViewBase):
    """ view on IForum 
        The ForumView is a collection of topics """

    def update(self):
        req = self.request
        if (req.has_key('preview') or req.has_key('cancel') or
                (not req.has_key('topic'))):
            return
        
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('Sorry you need to be authorized to use this '
                               'forum')
        topic = unicode(req['topic'], 'UTF-8')
        if not topic.strip():
            return 'Please provide a subject'
        
        try:
            self.context.add_topic(topic)
        except ValueError, e:
            return str(e)
        url = self.context.absolute_url()
        msg = 'Topic added'
        req.response.redirect('%s?message=%s' % (
                                self.context.absolute_url(),
                                quote(msg)))
        return ''

class TopicView(ViewBase):
    """ view on ITopic 
        The TopicView is a collection of comments """

    def update(self):
        req = self.request
        
        if (req.has_key('preview') or req.has_key('cancel') or
                (not req.has_key('title') and not req.has_key('text'))):
            return
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('Sorry, you need to be logged in to use '
                               'this forum')
        
        title = unicode(req['title'], 'UTF-8')
        text = unicode(req['text'], 'UTF-8')
        if not title.strip() and not text.strip():
            return 'Please fill in one of the two fields.'

        try:
            comment = self.context.add_comment(title, text)
        except ValueError, e:
            return str(e)

        msg = 'Comment added'
        numitems = self.context.number_of_comments()

        url = self.render_url(self.context.absolute_url(), 
                              message=msg,
                              batch_start=self.get_last_batch_start(numitems))

        req.response.redirect('%s#bottom' % url)
        return ''

class CommentView(ViewBase):
    pass

