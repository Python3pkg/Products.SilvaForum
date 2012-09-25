# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getMultiAdapter, getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import assertTriggersEvents, TestRequest
from Products.SilvaForum import interfaces
from Products.SilvaForum.views import replace_links
from Products.SilvaForum.testing import FunctionalLayer
from Products.SilvaMetadata.interfaces import IMetadataService


class SilvaForumTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaForum']
        factory.manage_addForum('forum', 'Forum')


class ForumTest(SilvaForumTestCase):

    def test_metadata_installed(self):
        metadata = getUtility(IMetadataService)
        self.assertEquals(
            metadata.getMetadataValue(
                self.root.forum, 'silvaforum-forum', 'do_not_exist'),
            None)
        self.assertEquals(
            metadata.getMetadataValue(
                self.root.forum, 'silvaforum-forum', 'anonymous_posting'),
            'no')
        self.assertEquals(
            metadata.getMetadataValue(
                self.root.forum, 'silvaforum-forum', 'unauthenticated_posting'),
            'no')

    def test_topics(self):
        forum = self.root.forum
        self.assertTrue(verifyObject(interfaces.IForum, forum))
        self.assertEqual(0, len(forum.topics()))

        factory = forum.manage_addProduct['SilvaForum']
        with assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addTopic('topic', 'Topic')

        self.assertEqual(1, len(forum.topics()))

    def test_add_topic(self):
        forum = self.root.forum
        # see if the forum is empty like we expect
        self.assertEqual(0, len(forum.objectValues('Silva Forum Topic')))

        # use our method to add a topic
        with assertTriggersEvents('ContentCreatedEvent'):
            newtopic = forum.add_topic('Topic')

        # see if the topic has been added properly
        self.assertEqual(1, len(forum.objectValues('Silva Forum Topic')))

        # also see if the thing returned is what we expect it is
        self.assertEqual('Silva Forum Topic', newtopic.meta_type)
        self.assertEqual('Topic', newtopic.get_title())

    def test_generate_id(self):
        forum = self.root.forum
        # test id uniqueness
        with assertTriggersEvents('ContentCreatedEvent'):
            topic1 = forum.add_topic('this is title one')
        with assertTriggersEvents('ContentCreatedEvent'):
            topic2 = forum.add_topic('this is title one')
        self.assertNotEqual(topic1.id, topic2.id)

        # test unicode strings
        test_id = 'ümlauts ümlauts'
        gen_id = forum._generate_id('ümlauts ümlauts')
        self.assertNotEqual(gen_id, test_id)

        # test invalid characters
        test_id = 'What the @#@%##!!$#%^'
        gen_id = forum._generate_id(test_id)
        self.assertNotEqual(gen_id, test_id)

        with assertTriggersEvents('ContentCreatedEvent'):
            t1 = forum.add_topic(':) foo :)')
            self.assertEqual('foo_', t1.id)

        with assertTriggersEvents('ContentCreatedEvent'):
            t2 = forum.add_topic(':) foo :)')
            self.assertEqual('foo__2', t2.id)

        with assertTriggersEvents('ContentCreatedEvent'):
            t3 = forum.add_topic(':) foo :)')
            self.assertEqual('foo__3', t3.id)

    def test_add_topic_anonymous(self):
        forum = self.root.forum
        self.assertFalse(forum.anonymous_posting_allowed())
        self.assertRaises(ValueError, forum.add_topic, 'Foo bar!', True)

        metadata = getUtility(IMetadataService)
        binding = metadata.getMetadata(forum)
        binding.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})
        with assertTriggersEvents('ContentCreatedEvent'):
            topic = forum.add_topic('Foo bar!', True)

        binding = metadata.getMetadata(topic)
        topics = forum.topics()
        self.assertEqual(binding.get('silvaforum-item', 'anonymous'), 'yes')
        self.assertEqual(topics[0]['creator'], 'anonymous')

    def test_not_anonymous(self):
        forum = self.root.forum
        metadata = getUtility(IMetadataService)
        with assertTriggersEvents('ContentCreatedEvent'):
            topic = forum.add_topic('Spam and eggs')

        binding = metadata.getMetadata(topic)
        topics = forum.topics()
        self.assertEqual(binding.get('silvaforum-item', 'anonymous'), 'no')
        self.assertEquals(topics[0]['creator'], 'author')

    def test_topic_indexing(self):
        forum = self.root.forum
        topic = forum.add_topic('This is a great topic.')

        catalog = self.root.service_catalog
        brains = catalog.searchResults(fulltext='great')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), topic)


class TopicTest(SilvaForumTestCase):

    def setUp(self):
        super(TopicTest, self).setUp()
        factory = self.root.forum.manage_addProduct['SilvaForum']
        factory.manage_addTopic('topic', 'Topic')

    def test_comments(self):
        topic = self.root.forum.topic
        self.assertTrue(verifyObject(interfaces.ITopic, topic))
        self.assertEquals(0, len(topic.comments()))

        factory = topic.manage_addProduct['SilvaForum']
        with assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addComment('com', 'Comment')

        self.assertEquals(1, len(topic.comments()))

    def test_add_comment(self):
        topic = self.root.forum.topic
        # test if the forum is empty
        self.assertEqual(0, len(topic.objectValues('Silva Forum Comment')))

        # test add_comment method
        with assertTriggersEvents('ContentCreatedEvent'):
            topic.add_comment('Comment', 'comment text')

        # see if the comment has been added properly
        self.assertEqual(1,len(topic.objectValues('Silva Forum Comment')))

    def test_not_anonymous(self):
        topic = self.root.forum.topic
        metadata = getUtility(IMetadataService)

        comment = topic.add_comment('Foo', 'Foo, bar and baz!')
        binding = metadata.getMetadata(comment)
        self.assertNotEqual(comment.get_creator(), 'anonymous')
        self.assertEqual(binding.get('silvaforum-item', 'anonymous'), 'no')
        self.assertEqual(topic.comments()[0]['creator'], 'author')

    def test_anonymous_not_allowed(self):
        topic = self.root.forum.topic
        metadata = getUtility(IMetadataService)

        binding = metadata.getMetadata(self.root.forum)
        self.assertEqual(
            binding.get('silvaforum-forum', 'anonymous_posting'), 'no')
        self.assertRaises(
            ValueError, topic.add_comment, 'comment', 'Comment', True)

    def test_anonymous(self):
        topic = self.root.forum.topic
        metadata = getUtility(IMetadataService)
        binding = metadata.getMetadata(self.root.forum)
        binding.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        comment = topic.add_comment('Foo', 'Foo, bar and baz', True)
        binding = metadata.getMetadata(comment)
        self.assertEqual(binding.get('silvaforum-item', 'anonymous'), 'yes')
        self.assertEqual(topic.comments()[-1]['creator'], 'anonymous')

    def test_comment_indexing(self):
        topic = self.root.forum.topic
        comment = topic.add_comment('Last comment', 'About indexing')

        catalog = self.root.service_catalog
        brains = catalog.searchResults(fulltext='indexing')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), comment)


class TopicViewTest(SilvaForumTestCase):

    def setUp(self):
        super(TopicViewTest, self).setUp()
        factory = self.root.forum.manage_addProduct['SilvaForum']
        factory.manage_addTopic('topic', 'Topic')

    def test_unicode_form_save_problems(self):
        view = getMultiAdapter(
            (self.root.forum.topic, TestRequest()),
            name=u'content.html')

        view.request.form['title'] = u'F\u00fb'.encode('UTF-8')
        view.request.form['text'] = u'b\u00e4r'.encode('UTF-8')

        view.update()


class CommentTest(SilvaForumTestCase):

    def setUp(self):
        super(CommentTest, self).setUp()
        factory = self.root.forum.manage_addProduct['SilvaForum']
        factory.manage_addTopic('topic', 'Topic')
        factory = self.root.forum.topic.manage_addProduct['SilvaForum']
        factory.manage_addComment('com', 'Comment')

    def test_comment(self):
        comment = self.root.forum.topic.com

        self.assertTrue(verifyObject(interfaces.IComment, comment))
        self.assertEquals('Comment', comment.get_title())
        self.assertEquals('', comment.get_text())

        comment.set_text('foo text')
        self.assertEquals('foo text', comment.get_text())


class CommentViewTest(SilvaForumTestCase):

    def setUp(self):
        super(CommentViewTest, self).setUp()
        factory = self.root.forum.manage_addProduct['SilvaForum']
        factory.manage_addTopic('topic', 'Topic')
        factory = self.root.forum.topic.manage_addProduct['SilvaForum']
        factory.manage_addComment('com', 'Comment')

    def test_format_text(self):
        view = getMultiAdapter(
            (self.root.forum.topic.com, TestRequest()),
            name=u'content.html')
        view.update()

        self.assertEqual('foo bar', view.format_text('foo bar'))
        self.assertEqual('foo<br />bar', view.format_text('foo\nbar'))
        self.assertEquals('foo&lt;bar', view.format_text('foo<bar'))

class ReplaceLinkTestCase(unittest.TestCase):

    def test_replace_links(self):

        text = 'aaa aaa www.link.org aaa'
        self.assertEquals(
            'aaa aaa <a href="http://www.link.org">www.link.org</a> aaa',
            replace_links(text))
        text = 'aa aa http://www.link.org a'
        self.assertEquals(
            'aa aa <a href="http://www.link.org">http://www.link.org</a> a',
            replace_links(text))
        text = 'aa aa http://link.org a'
        self.assertEquals(
            'aa aa <a href="http://link.org">http://link.org</a> a',
            replace_links(text))
        text = 'aa aa https://www.security.org a'
        self.assertEquals(
            'aa aa <a href="https://www.security.org">https://www.security.org</a> a',
            replace_links(text))
        text = 'aa aa mailto:myemail@myemail.com a'
        self.assertEquals(
            'aa aa <a href="mailto:myemail@myemail.com">mailto:myemail@myemail.com</a> a',
            replace_links(text))
        text = 'www.link.org.'
        self.assertEquals(
            '<a href="http://www.link.org">www.link.org</a>.',
            replace_links(text))
        text = '(www.link.org)'
        self.assertEquals(
            '(<a href="http://www.link.org">www.link.org</a>)',
            replace_links(text))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReplaceLinkTestCase))
    suite.addTest(unittest.makeSuite(ForumTest))
    suite.addTest(unittest.makeSuite(TopicTest))
    suite.addTest(unittest.makeSuite(TopicViewTest))
    suite.addTest(unittest.makeSuite(CommentTest))
    suite.addTest(unittest.makeSuite(CommentViewTest))
    return suite
