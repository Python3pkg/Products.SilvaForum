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

    def format_text(self, title):
        title = mangle.entities(title)
        root = self.context.aq_inner.get_root()
        title = emoticons(title,
            self.get_resources().emoticons.smilies.absolute_url())
        title = title.replace('\n', '<br />')
        return title

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

        req.response.redirect('%s?message=%s' % (self.context.absolute_url(),
                                                 quote(msg)))
        return msg

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

        comment = self.context.add_comment(title, text)

        url = self.context.absolute_url()
        msg = 'Comment added'
        
        req.response.redirect('%s?message=%s' % (self.context.absolute_url(),
                                                 quote(msg)))
        return msg

class CommentView(ViewBase):
    pass

