# Copyright (c) 2007 Infrae. All rights reserved.
# See also LICENSE.txt
import SilvaTestCase
from Testing.ZopeTestCase import utils
from zope.component import getMultiAdapter
from datetime import datetime
from DateTime.DateTime import DateTime
import os

test_path = os.path.dirname(__file__)

class ForumTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum',
                                    title='Forum', product='SilvaForum')
    
    def test_threads(self):
        self.assertEquals(0, len(self.forum.threads()))
        
        self.thread1 = self.addObject(self.forum, 'Thread', 'thread1',
                                      title='Thread 1', product='SilvaForum')
        self.assertEquals(1, len(self.forum.threads()))
    
    def test_add_thread(self):
        # see if the forum is empty like we expect
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Thread')))

        # use our method to add a thread
        newthread = self.forum.add_thread('Topic', 'topic text')

        # see if the thread has been added properly
        self.assertEquals(1,
                len(self.forum.objectValues('Silva Forum Thread')))

        # also see if the thing returned is what we expect it is
        self.assertEquals('Silva Forum Thread', newthread.meta_type)
        self.assertEquals(getattr(self.forum, newthread.id).absolute_url(),
                          newthread.absolute_url())
        self.assertEquals('topic text', newthread.get_text())

    def test_generate_id(self):
        from Products.SilvaForum.content import _generate_id
        class FakeObj(object):
            def __init__(self):
                self._lastid = 0
        f = FakeObj()
        previd = f._lastid
        id1 = _generate_id(f)
        setattr(f, id1, 1) # required to find out whether an id is unique
        self.assertNotEquals(id1, previd)
        f._lastid = previd
        id2 = _generate_id(f)
        setattr(f, id2, 1)
        self.assertNotEquals(id1, previd)
        self.assertNotEquals(id2, id1)

class ThreadTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum',
                                    title='Forum', product='SilvaForum')
        self.thread = self.addObject(self.forum, 'Thread', 'thread',
                                     title='Thread', product='SilvaForum')
    
    def test_comments(self):
        self.assertEquals(0, len(self.thread.comments()))
        
        self.comment1 = self.addObject(self.thread, 'Comment', 'comment1',
                                       title='Comment 1', product='SilvaForum')
        self.assertEquals(1, len(self.thread.comments()))
    
    def test_add_comment(self):
        # test if the forum is empty
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Comment')))

        # test add_comment method
        newcomment = self.thread.add_comment('Comment', 'comment text')
        
        # see if the comment has been added properly
        self.assertEquals(1,
                len(self.thread.objectValues('Silva Forum Comment')))

class ThreadViewTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum1',
                                    title='Forum', product='SilvaForum')
        self.thread = self.addObject(self.forum, 'Thread', 'thread1',
                                     title='Thread', product='SilvaForum')
        self.view = getMultiAdapter((self.thread, self.app.REQUEST),
                                    name=u'index.html')

    def test_format_datetime(self):
        # XXX this needs to either be removed, or test something useful...
        dt = DateTime('2007/01/01 01:00')
        self.assertEquals('2007/01/01 01:00:00 GMT+1',
                          self.view.format_datetime(dt))

    def test_unicode_form_save_problems(self):
        self.view.request['title'] = u'F\u00fb'.encode('UTF-8')
        self.view.request['text'] = u'b\u00e4r'.encode('UTF-8')

        self.view.update()

class CommentTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum1',
                                    title='Forum', product='SilvaForum')
        self.thread = self.addObject(self.forum, 'Thread', 'thread1',
                                     title='Thread', product='SilvaForum')
        self.comment = self.addObject(self.thread, 'Comment', 'comment1',
                                      title='Comment', product='SilvaForum')

    def test_comment(self):
        self.assertEquals('Comment', self.comment.get_title())
        self.assertEquals('', self.comment.get_text())

        self.comment.set_text('foo text')
        self.assertEquals('foo text', self.comment.get_text())

class CommentViewTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum1',
                                    title='Forum', product='SilvaForum')
        self.thread = self.addObject(self.forum, 'Thread', 'thread1',
                                     title='Thread', product='SilvaForum')
        self.comment = self.addObject(self.thread, 'Comment', 'comment1',
                                      title='Comment', product='SilvaForum')
        self.view = getMultiAdapter((self.comment, self.app.REQUEST),
                                    name=u'index.html')

    def test_format_text(self):
        text = 'foo bar'
        self.assertEquals('foo bar', self.view.format_text(text))
        text = 'foo\nbar'
        self.assertEquals('foo<br />bar', self.view.format_text(text))
        text = 'foo<bar'
        self.assertEquals('foo&lt;bar', self.view.format_text(text))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumTest))
    suite.addTest(unittest.makeSuite(ThreadTest))
    suite.addTest(unittest.makeSuite(ThreadViewTest))
    suite.addTest(unittest.makeSuite(CommentTest))
    suite.addTest(unittest.makeSuite(CommentViewTest))
    return suite

