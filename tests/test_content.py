# -*- coding: utf-8 -*-
# $Id$

from zope.component import getMultiAdapter, getUtility
from zope.interface.verify import verifyObject

from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaForum import interfaces
from Products.Silva.tests import SilvaTestCase

from Testing import ZopeTestCase

ZopeTestCase.installProduct('SilvaForum')


class SilvaForumTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.root.service_extensions.install('SilvaForum')
        self.forum = self.addObject(
            self.silva, 'Forum', 'forum',
            title='Forum', product='SilvaForum')


class ForumTest(SilvaForumTestCase):

    def test_metadata_set_installed(self):
        metadata = getUtility(IMetadataService)
        self.assertRaises(
            Exception, metadata.getMetadataValue, self.forum,
            'silvaforum-forum', 'thisdoesnotexist')
        self.assertEquals(metadata.getMetadataValue(
                self.forum, 'silvaforum-forum', 'anonymous_posting'), 'no')

    def test_uninstall_metadata(self):
        from Products.SilvaForum.install import unconfigureMetadata
        metadata = getUtility(IMetadataService)
        self.failUnless(
            'silvaforum-forum' in metadata.getCollection().objectIds())
        unconfigureMetadata(self.root)
        self.failIf(
            'silvaforum-forum' in metadata.getCollection().objectIds())

    def test_topics(self):
        #self.failUnless(verifyObject(interfaces.IForum, self.forum))

        self.assertEquals(0, len(self.forum.topics()))

        self.topic1 = self.addObject(
            self.forum, 'Topic', 'topic1',
            title='Topic 1', product='SilvaForum')
        self.assertEquals(1, len(self.forum.topics()))

    def test_add_topic(self):
        # see if the forum is empty like we expect
        self.assertEquals(
            0, len(self.forum.objectValues('Silva Forum Topic')))

        # use our method to add a topic
        newtopic = self.forum.add_topic('Topic')

        # see if the topic has been added properly
        self.assertEquals(
            1, len(self.forum.objectValues('Silva Forum Topic')))

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

        t1 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo_', t1.id)

        t2 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo__2', t2.id)

        t3 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo__3', t3.id)

    def test_add_topic_anonymous(self):
        self.assertFalse(self.forum.anonymous_posting_allowed())
        self.assertRaises(
            ValueError, self.forum.add_topic, 'Foo bar!', True)

        metadata = getUtility(IMetadataService)
        binding = metadata.getMetadata(self.forum)
        binding.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})
        topic = self.forum.add_topic('Foo bar!', True)

        binding = metadata.getMetadata(topic)
        self.failUnless(binding.get('silvaforum-item', 'anonymous') == 'yes')
        topics = self.forum.topics()
        self.assertEquals(topics[0]['creator'], 'anonymous')

    def test_not_anonymous(self):
        metadata = getUtility(IMetadataService)
        topic = self.forum.add_topic('Spam and eggs')
        self.assert_(metadata.getMetadataValue(
                topic, 'silvaforum-item', 'anonymous') == 'no')
        topics = self.forum.topics()
        self.assertEquals(topics[0]['creator'], 'test_user_1_')

    def test_topic_indexing(self):
        topic = self.forum.add_topic('This is a great topic.')

        catalog = self.root.service_catalog
        brains = catalog.searchResults(fulltext='great')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), topic)


class TopicTest(SilvaForumTestCase):

    def afterSetUp(self):
        super(TopicTest, self).afterSetUp()
        self.topic = self.addObject(
            self.forum, 'Topic', 'topic', title='Topic', product='SilvaForum')

    def test_comments(self):
        #self.failUnless(verifyObject(interfaces.ITopic, self.topic))

        self.assertEquals(0, len(self.topic.comments()))

        self.comment1 = self.addObject(
            self.topic, 'Comment', 'comment1',
            title='Comment 1', product='SilvaForum')
        self.assertEquals(1, len(self.topic.comments()))

    def test_add_comment(self):
        # test if the forum is empty
        self.assertEquals(
            0, len(self.forum.objectValues('Silva Forum Comment')))

        # test add_comment method
        self.topic.add_comment('Comment', 'comment text')

        # see if the comment has been added properly
        self.assertEquals(1,
                len(self.topic.objectValues('Silva Forum Comment')))

    def test_not_anonymous(self):
        metadata = getUtility(IMetadataService)

        comment = self.topic.add_comment('Foo', 'Foo, bar and baz!')
        self.assert_(comment.get_creator() != 'anonymous')
        self.assertEquals(metadata.getMetadataValue(
                comment, 'silvaforum-item', 'anonymous'), 'no')
        self.assertEquals(self.topic.comments()[0]['creator'], 'test_user_1_')

    def test_anonymous_not_allowed(self):
        metadata = getUtility(IMetadataService)

        self.assertEqual(metadata.getMetadataValue(
                self.forum, 'silvaforum-forum', 'anonymous_posting'), 'no')
        self.assertRaises(
            ValueError, self.topic.add_comment,
            'Foo', 'Foo, bar and baz', True)

    def test_anonymous(self):
        metadata = getUtility(IMetadataService)
        binding = metadata.getMetadata(self.forum)
        binding.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        comment = self.topic.add_comment('Foo', 'Foo, bar and baz', True)
        binding = metadata.getMetadata(comment)
        self.assertEquals(binding.get('silvaforum-item', 'anonymous'), 'yes')
        self.assertEquals(self.topic.comments()[-1]['creator'], 'anonymous')

    def test_comment_indexing(self):
        comment = self.topic.add_comment('Last comment', 'About indexing')

        catalog = self.root.service_catalog
        brains = catalog.searchResults(fulltext='indexing')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), comment)


class TopicViewTest(SilvaForumTestCase):

    def afterSetUp(self):
        super(TopicViewTest, self).afterSetUp()
        self.topic = self.addObject(
            self.forum, 'Topic', 'topic1', title='Topic', product='SilvaForum')
        self.view = getMultiAdapter(
            (self.topic, self.app.REQUEST), name=u'content.html')

    def test_unicode_form_save_problems(self):
        self.view.request['title'] = u'F\u00fb'.encode('UTF-8')
        self.view.request['text'] = u'b\u00e4r'.encode('UTF-8')

        self.view.update()


class CommentTest(SilvaForumTestCase):

    def afterSetUp(self):
        super(CommentTest, self).afterSetUp()
        self.topic = self.addObject(
            self.forum, 'Topic', 'topic1', title='Topic', product='SilvaForum')
        self.comment = self.addObject(
            self.topic, 'Comment', 'comment1',
            title='Comment', product='SilvaForum')

    def test_comment(self):
        self.failUnless(verifyObject(interfaces.IComment, self.comment))

        self.assertEquals('Comment', self.comment.get_title())
        self.assertEquals('', self.comment.get_text())

        self.comment.set_text('foo text')
        self.assertEquals('foo text', self.comment.get_text())


class CommentViewTest(SilvaForumTestCase):
    def afterSetUp(self):
        super(CommentViewTest, self).afterSetUp()
        self.topic = self.addObject(
            self.forum, 'Topic', 'topic1', title='Topic', product='SilvaForum')
        self.comment = self.addObject(
            self.topic, 'Comment', 'comment1',
            title='Comment', product='SilvaForum')
        self.view = getMultiAdapter(
            (self.comment, self.app.REQUEST), name=u'content.html')

    def test_format_text(self):
        text = 'foo bar'
        self.assertEquals('foo bar', self.view.format_text(text))
        text = 'foo\nbar'
        self.assertEquals('foo<br />bar', self.view.format_text(text))
        text = 'foo<bar'
        self.assertEquals('foo&lt;bar', self.view.format_text(text))

    def test_replace_links(self):
        text = 'aaa aaa www.link.org aaa'
        self.assertEquals(
            'aaa aaa <a href="http://www.link.org">www.link.org</a> aaa',
            self.view.replace_links(text))
        text = 'aa aa http://www.link.org a'
        self.assertEquals(
            'aa aa <a href="http://www.link.org">http://www.link.org</a> a',
            self.view.replace_links(text))
        text = 'aa aa http://link.org a'
        self.assertEquals(
            'aa aa <a href="http://link.org">http://link.org</a> a',
            self.view.replace_links(text))
        text = 'aa aa https://www.security.org a'
        self.assertEquals(
            'aa aa <a href="https://www.security.org">https://www.security.org</a> a',
            self.view.replace_links(text))
        text = 'aa aa mailto:myemail@myemail.com a'
        self.assertEquals(
            'aa aa <a href="mailto:myemail@myemail.com">mailto:myemail@myemail.com</a> a',
            self.view.replace_links(text))
        text = 'www.link.org.'
        self.assertEquals(
            '<a href="http://www.link.org">www.link.org</a>.',
            self.view.replace_links(text))
        text = '(www.link.org)'
        self.assertEquals(
            '(<a href="http://www.link.org">www.link.org</a>)',
            self.view.replace_links(text))


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumTest))
    suite.addTest(unittest.makeSuite(TopicTest))
    suite.addTest(unittest.makeSuite(TopicViewTest))
    suite.addTest(unittest.makeSuite(CommentTest))
    suite.addTest(unittest.makeSuite(CommentViewTest))
    return suite
