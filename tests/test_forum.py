# Copyright (c) 2007 Infrae. All rights reserved.
# See also LICENSE.txt
# SilvaForum
# Python

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
    
    def test_topics(self):
        self.assertEquals(0, len(self.forum.topics()))
        
        self.topic1 = self.addObject(self.forum, 'Topic', 'topic1',
                                      title='Topic 1', product='SilvaForum')
        self.assertEquals(1, len(self.forum.topics()))
    
    def test_add_topic(self):
        # see if the forum is empty like we expect
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Topic')))

        # use our method to add a topic
        newtopic = self.forum.add_topic('Topic')

        # see if the topic has been added properly
        self.assertEquals(1,
                len(self.forum.objectValues('Silva Forum Topic')))

        # also see if the thing returned is what we expect it is
        self.assertEquals('Silva Forum Topic', newtopic.meta_type)
        self.assertEquals(getattr(self.forum, newtopic.id).absolute_url(),
                          newtopic.absolute_url())
        self.assertEquals('Topic', newtopic.get_title())
        
        # test id uniqueness
        topic1 = self.forum.add_topic('this is title one')
        topic2 = self.forum.add_topic('this is title one')
        self.assertNotEquals(topic1.id, topic2.id)

    def test_generate_id(self):
        # test double strings
        topic1 = self.forum.add_topic('test one')
        topic2 = self.forum.add_topic('test one')
        self.assertNotEquals(topic1.id, topic2.id)
        
        # test unicode strings
        test_id = 'ümlauts ümlauts'
        gen_id = self.forum._generate_id('ümlauts ümlauts')
        self.assertNotEquals(gen_id, test_id)

        # test invalid characters
        test_id = 'What the @#@%##!!$#%^'
        gen_id = self.forum._generate_id(test_id)
        self.assertNotEquals(gen_id, test_id)

class TopicTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum',
                                    title='Forum', product='SilvaForum')
        self.topic = self.addObject(self.forum, 'Topic', 'topic',
                                     title='Topic', product='SilvaForum')
    
    def test_comments(self):
        self.assertEquals(0, len(self.topic.comments()))
        
        self.comment1 = self.addObject(self.topic, 'Comment', 'comment1',
                                       title='Comment 1', product='SilvaForum')
        self.assertEquals(1, len(self.topic.comments()))
    
    def test_add_comment(self):
        # test if the forum is empty
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Comment')))

        # test add_comment method
        newcomment = self.topic.add_comment('Comment', 'comment text')
        
        # see if the comment has been added properly
        self.assertEquals(1,
                len(self.topic.objectValues('Silva Forum Comment')))
    
class TopicViewTest(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum1',
                                    title='Forum', product='SilvaForum')
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                     title='Topic', product='SilvaForum')
        self.view = getMultiAdapter((self.topic, self.app.REQUEST),
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
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                     title='Topic', product='SilvaForum')
        self.comment = self.addObject(self.topic, 'Comment', 'comment1',
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
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                     title='Topic', product='SilvaForum')
        self.comment = self.addObject(self.topic, 'Comment', 'comment1',
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
    suite.addTest(unittest.makeSuite(TopicTest))
    suite.addTest(unittest.makeSuite(TopicViewTest))
    suite.addTest(unittest.makeSuite(CommentTest))
    suite.addTest(unittest.makeSuite(CommentViewTest))
    return suite

