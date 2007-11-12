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
    
    def get_batch_first_link(self, current_offset):
        if current_offset == 0:
            return
        return self.context.absolute_url() + '?batch_start=0'

    def get_last_batch_start(self):
        # returns the offset number of the last batch page
        # this should be implemented by a specific subclass
        raise NotImplementedError


    def get_batch_last_link(self, current_offset):
        offset = self.get_last_batch_start()
        if current_offset == offset:
            return
        return self.context.absolute_url() + '?batch_start=' + str(offset)

    def format_text(self, text):
        text = mangle.entities(text)
        root = self.context.aq_inner.get_root()
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

    def trigger_sec(self):
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('Sorry you need to be authorized to use this '
                               'forum')

    def get_resources(self):
        return self.context.aq_inner.get_root().service_resources.SilvaForum

class ForumView(ViewBase):
    """ view on IForum 
        The ForumView is a collection of topics """

    def get_topics(self):
        topics = self.context.topics()
        topics.reverse()
        return topics

    def get_last_batch_start(self):
        batchlength = self.context.number_of_topics()
        size = self.context.topic_batch_size
        rest = batchlength % size
        offset = batchlength - rest
        # if rest is 0, then the last batch page would be empty,
        # so we show the batch page before that
        if rest == 0:
            offset -= size
        return offset
    
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
        self.context.add_topic(topic)
        url = self.context.absolute_url()
        msg = 'Topic added'
        

        req.response.redirect('%s?message=%s' % (
                                self.context.absolute_url(),
                                quote(msg)))
        #req.response.redirect('%s?message=%s&batch_start=%s#bottom' % (
        #                        self.context.absolute_url(),
        #                        quote(msg),
        #                        self.get_last_batch_start()))
        return msg

class TopicView(ViewBase):
    """ view on ITopic 
        The TopicView is a collection of comments """

    def get_last_batch_start(self):
        batchlength = self.context.number_of_comments()
        size = self.context.comment_batch_size
        rest = batchlength % size
        offset = batchlength - rest
        # if rest is 0, then the last batch page would be empty,
        # so we show the batch page before that
        if rest == 0:
            offset -= size
        return offset

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

        comment = self.context.add_comment(title, text)

        url = self.context.absolute_url()
        msg = 'Comment added'
        req.response.redirect('%s?message=%s&batch_start=%s#bottom' % (
                                self.context.absolute_url(),
                                quote(msg),
                                self.get_last_batch_start()))
        return msg

class CommentView(ViewBase):
    pass

