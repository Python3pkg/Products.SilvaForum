from Products.Five import BrowserView
from Products.Silva.browser.headers import Headers
from Products.Silva import mangle
from Products.SilvaForum.emoticons.emoticons import emoticons, smileydata
from Products.SilvaForum.dtformat.dtformat import format_dt
from DateTime import DateTime
from AccessControl import getSecurityManager, Unauthorized

from urllib import quote

minimal_add_role = 'Authenticated'

class ViewBase(Headers):
    def format_datetime(self, dt):
        return format_dt(dt, DateTime())

    def format_text(self, text):
        text = mangle.entities(text)
        text = emoticons(text,
                         self.context.get_root().service_smilies.absolute_url())
        text = text.replace('\n', '<br />')
        return text

    def get_smiley_data(self):
        ret = []
        service_url = self.context.get_root().service_smilies.absolute_url()
        for image, smileys in smileydata.items():
            ret.append({
                'text': smileys[0],
                'href': service_url + '/' + image,
            })
        return ret

class ForumView(ViewBase):
    """ view on IForum 
        The ForumView is a collection of threads """

    def update(self):
        req = self.request
        if (req.has_key('preview') or req.has_key('cancel') or
                (not req.has_key('topic') and not req.has_key('text'))):
            return
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('Sorry you need to be authorized to use this '
                               'forum')
        topic = unicode(req['topic'], 'UTF-8')
        if not topic.strip():
            return 'Please provide a subject'
        text = unicode(req['text'], 'UTF-8')

        self.context.add_thread(topic, text)
        url = self.context.absolute_url()
        msg = 'Topic added'

        req.response.redirect('%s?message=%s' % (self.context.absolute_url(),
                                                 quote(msg)))
        return msg

class ThreadView(ViewBase):
    """ view on IThread 
        The ThreadView is a collection of comments """

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

