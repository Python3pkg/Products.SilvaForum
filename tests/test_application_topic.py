# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest

from zope.component import getUtility

from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaForum.testing import FunctionalLayer


class TopicFunctionalTestCase(unittest.TestCase):
    """Functional test for Silva Forum.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaForum']
        factory.manage_addForum('forum', 'Test Forum')
        factory = self.root.forum.manage_addProduct['SilvaForum']
        factory.manage_addTopic('topic', 'Test Topic')

    def test_login_and_post_comment(self):
        """Login to post a new comment in a topic.
        """
        browser = self.layer.get_browser()
        browser.inspect.add('feedback', '//div[@class="feedback"]/span')
        browser.inspect.add('title', '//div[@id="content"]/descendant::h2')
        browser.inspect.add('author', '//span[@class="author"]')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.title, ['Test Forum'])
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.assertFalse("Post a new comment" in browser.contents)
        browser.login('dummy', 'dummy')
        browser.reload()

        self.assertTrue("Post a new comment" in browser.contents)
        form = browser.get_form('postcomment')

        # You can now add a topic
        form.get_control("title").value = "New Comment"
        form.get_control("text").value = "It's about a product for forum"
        self.assertEqual(form.get_control("submit").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added"])
        self.assertEqual(browser.inspect.author[-1], "dummy")
        self.assertTrue("New Comment" in browser.contents)
        self.assertTrue("It's about a product for forum" in browser.contents)

        self.assertEqual(browser.get_link("posted").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic/New_Comment")
        self.assertEqual(browser.get_link("Up to topic...").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic")

    def test_post_comment_as_anonymous(self):
        """Post a new comment as anonymous
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        browser = self.layer.get_browser()
        browser.inspect.add('feedback', '//div[@class="feedback"]/span')
        browser.inspect.add('author', '//span[@class="author"]')
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        form = browser.get_form('postcomment')
        form.get_control("title").value = "Anonymous Comment"
        form.get_control("text").value = "It's a secret"
        form.get_control("anonymous").checked = True
        self.assertEqual(form.get_control("submit").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added"])
        self.assertEqual(browser.inspect.author[-1], "anonymous")
        self.assertEqual(browser.get_link("posted").click(), 200)
        self.assertEqual(
            browser.location, "/root/forum/topic/Anonymous_Comment")

    def test_topic_post_validation(self):
        """Try to add an empty comment.
        """
        browser = self.layer.get_browser()
        browser.inspect.add('feedback', '//div[@class="feedback"]/span')
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)
        self.assertEqual(browser.inspect.feedback, [])

        form = browser.get_form('postcomment')
        self.assertEqual(form.get_control("submit").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a title and a text"])

    def test_topic_preview_validation(self):
        """Try to preview an empty or incomplete comment.
        """
        browser = self.layer.get_browser()
        browser.inspect.add('feedback', '//div[@class="feedback"]/span')
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)
        self.assertEqual(browser.inspect.feedback, [])

        form = browser.get_form('postcomment')
        self.assertEqual(form.get_control("preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new comment",
             "Please provide a message for the new comment"])

        form = browser.get_form('postcomment')
        form.get_control('title').value = 'Previewed comment'
        self.assertEqual(form.get_control("preview").click(), 200)

        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a message for the new comment"])
        form = browser.get_form('postcomment')
        self.assertEqual(form.get_control('title').value, 'Previewed comment')

        form.get_control('title').value = ''
        form.get_control('text').value = 'Previewed message'
        self.assertEqual(form.get_control("preview").click(), 200)

        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new comment"])
        form = browser.get_form('postcomment')
        self.assertEqual(form.get_control('text').value, 'Previewed message')

    def test_comment_preview_and_post(self):
        """Enter a comment, preview and post it.
        """
        browser = self.layer.get_browser()
        browser.login('dummy', 'dummy')
        browser.inspect.add('feedback', '//div[@class="feedback"]/span')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Add and preview a new comment
        self.assertTrue("Post a new comment" in browser.contents)
        form = browser.get_form('postcomment')
        form.get_control("title").value = "New Previewed Comment"
        form.get_control("text").value = "It's about a product for forum"
        self.assertEqual(form.get_control("preview").click(), 200)
        self.assertEqual(browser.inspect.feedback, [])

        form = browser.get_form('previewcomment')
        self.assertEqual(
            form.get_control('title').value, 'New Previewed Comment')
        self.assertEqual(
            form.get_control('text').value, "It's about a product for forum")
        self.assertEqual(form.get_control("post_comment").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added"])
        self.assertTrue("New Previewed Comment" in browser.contents)
        self.assertTrue("It's about a product for forum" in browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TopicFunctionalTestCase))
    return suite
