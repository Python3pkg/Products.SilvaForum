from Products.Five import BrowserView
from Products.Silva.browser.headers import Headers
from Products.Silva import mangle
from Products.SilvaForum.emoticons.emoticons import emoticons, smileydata
from Products.SilvaForum.dtformat.dtformat import format_dt
from DateTime import DateTime
from AccessControl import getSecurityManager, Unauthorized

from urllib import quote as urlquote

minimal_add_role = 'Authenticated'

# XXX hrmph, mixin :|
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
        # walk through the dict
        service_url = self.context.get_root().service_smilies.absolute_url()
        # implement length check
        # assign list of tuples
        # process the longest to the shortest index values
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
        if not req.has_key('topic') and not req.has_key('text'):
            return
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('need to be authenticated')
        topic = req['topic']
        if not topic.strip():
            return 'please provide a topic'
        text = req['text']
        if not text.strip():
            return 'please provide text'
        self.context.add_thread(topic, text)
        url = self.context.absolute_url()
        msg = urlquote('topic added')
        req.response.redirect('%s?message=%s' % (url, msg))

class ThreadView(ViewBase):
    """ view on IThread 
        The ThreadView is a collection of comments """

    def update(self):
        req = self.request
        if not req.has_key('title') and not req.has_key('text'):
            return
        sec = getSecurityManager()
        if not sec.getUser().has_role(minimal_add_role):
            raise Unauthorized('need to be authenticated')
        title = req['title']
        text = req['text']
        if not title.strip() or not text.strip():
            return 'title and text are both mandatory'
        comment = self.context.add_comment(title, text)
        url = self.context.absolute_url()
        msg = urlquote('comment added')
        req.response.redirect('%s?message=%s' % (url, msg))

class CommentView(ViewBase):
    pass

