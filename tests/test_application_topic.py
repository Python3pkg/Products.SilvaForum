# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest

from zope.publisher.browser import TestRequest
from zope.component import getUtility, getMultiAdapter

from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaForum.testing import FunctionalLayer


def topic_settings(browser):
    browser.inspect.add('feedback', '//div[@class="feedback"]/span')
    browser.inspect.add('title', '//div[@class="forum"]/descendant::h2')
    browser.inspect.add(
        'subjects',
        '//table[@class="forum-content-table"]//td[@class="comment"]//h5')
    browser.inspect.add(
        'comments',
        '//table[@class="forum-content-table"]'
        '//td[@class="comment"]/p[@class="comment"]')
    browser.inspect.add(
        'authors',
        '(//table[@class="forum-content-table"]//span[@class="author"])'
        '[position() > 1]')
    browser.inspect.add(
        'preview_subject',
        '//table[contains(@class,"forum-preview")]//td[@class="comment"]/h5')
    browser.inspect.add(
        'preview_comment',
        '//table[contains(@class,"forum-preview")]'
        '//td[@class="comment"]/p[@class="comment"]')
    browser.inspect.add(
        'preview_author',
        '//table[contains(@class,"forum-preview")]//p[@class="author"]/span')


def get_captcha_word(browser):
    request = TestRequest(HTTP_COOKIE=browser.get_request_header('Cookie'))
    captcha = getMultiAdapter((object(), request), name='captcha')
    return captcha._generate_words()[1]


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

    def test_login_and_post(self):
        """Login to post a new comment in a topic.
        """
        browser = self.layer.get_browser(topic_settings)

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.title, ['Test Forum'])
        self.assertEqual(browser.get_link('Test Topic').click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic")

        # By default there is no comments nor feedback
        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.assertFalse("Post a new comment" in browser.contents)
        self.assertRaises(AssertionError, browser.get_form, 'post')
        browser.login('dummy', 'dummy')
        browser.reload()

        self.assertTrue("Post a new comment" in browser.contents)
        form = browser.get_form('post')

        # There is anonymous or captcha option
        self.assertRaises(AssertionError, form.get_control, 'anonymous')
        self.assertRaises(AssertionError, form.get_control, 'captcha')

        # You can now add a topic
        form.get_control("title").value = "New Comment"
        form.get_control("text").value = "It's about a product for forum"
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added."])

        self.assertEqual(browser.inspect.subjects, ["New Comment"])
        self.assertEqual(browser.inspect.authors, ["dummy"])
        self.assertEqual(
            browser.inspect.comments,
            ["It's about a product for forum"])

        # And you can visit the comment
        self.assertEqual(browser.get_link("posted").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic/New_Comment")
        self.assertEqual(browser.get_link("Up to topic...").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic")

    def test_post_as_anonymous(self):
        """Post a new comment as anonymous
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Fill in and preview a new comment
        form = browser.get_form('post')
        self.assertEqual(form.get_control("anonymous").checked, False)
        form.get_control("title").value = "Anonymous Comment"
        form.get_control("text").value = "It's a secret"
        form.get_control("anonymous").checked = True
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_author, ['anonymous'])

        # Post the previewed comment
        form = browser.get_form('post')
        self.assertEqual(form.get_control("anonymous").checked, True)
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added."])
        self.assertEqual(browser.inspect.subjects, ["Anonymous Comment"])
        self.assertEqual(browser.inspect.comments, ["It's a secret"])
        self.assertEqual(browser.inspect.authors, ["anonymous"])

        self.assertEqual(browser.get_link("posted").click(), 200)
        self.assertEqual(
            browser.location,
            "/root/forum/topic/Anonymous_Comment")

    def test_post_preview_unauthenticated_with_captcha(self):
        """Activate unauthenicated posting and test that if you fill
        the captcha you can post unauthenticated.
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues(
            'silvaforum-forum',
            {'unauthenticated_posting': 'yes',
             'anonymous_posting': 'yes'})

        browser = self.layer.get_browser(topic_settings)
        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Fill and preview a comment
        form = browser.get_form('post')

        # There is no anonymous option
        self.assertRaises(AssertionError, form.get_control, 'anonymous')

        form.get_control("title").value = "Hello John"
        form.get_control("text").value = "I am Henri"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_author, ['anonymous'])
        self.assertEqual(browser.inspect.preview_subject, ['Hello John'])
        self.assertEqual(browser.inspect.preview_comment, ['I am Henri'])

        # Try to post the previewed comment without filling the captcha
        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Invalid captcha value"])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.preview_subject, [])
        self.assertEqual(browser.inspect.preview_comment, [])
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

        # Filling the captcha and post
        form = browser.get_form('post')
        form.get_control("captcha").value = get_captcha_word(browser)
        self.assertEqual(form.get_control("title").value, "Hello John")
        self.assertEqual(form.get_control("text").value, "I am Henri")
        self.assertEqual(form.get_control("action.post").click(), 200)

        # And the comment is added
        self.assertEqual(browser.inspect.feedback, ["Comment added."])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.preview_subject, [])
        self.assertEqual(browser.inspect.preview_comment, [])
        self.assertEqual(browser.inspect.subjects, ['Hello John'])
        self.assertEqual(browser.inspect.comments, ['I am Henri'])
        self.assertEqual(browser.inspect.authors, ['anonymous'])

    def test_post_authenticated_with_captcha(self):
        """Activate unauthenicated posting and test that you have no
        captcha for authenticated users.
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues(
            'silvaforum-forum',
            {'unauthenticated_posting': 'yes',
             'anonymous_posting': 'yes'})

        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Post a new comment
        form = browser.get_form('post')
        form.get_control("title").value = "Hello Henri"
        form.get_control("text").value = "I am Dummy"
        self.assertEqual(form.get_control('anonymous').checked, False)

        # There is no captcha field.
        self.assertRaises(AssertionError, form.get_control, 'captcha')

        self.assertEqual(form.get_control("action.post").click(), 200)

        # And the comment is added
        self.assertEqual(browser.inspect.feedback, ["Comment added."])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.preview_subject, [])
        self.assertEqual(browser.inspect.preview_comment, [])
        self.assertEqual(browser.inspect.subjects, ['Hello Henri'])
        self.assertEqual(browser.inspect.comments, ['I am Dummy'])
        self.assertEqual(browser.inspect.authors, ['dummy'])

    def test_post_validation(self):
        """Try to add an empty comment.
        """
        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.post").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject and a message."])

        # Noting is created
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

    def test_preview_validation(self):
        """Try to preview an empty or incomplete comment.
        """
        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new comment.",
             "Please provide a message for the new comment."])

        form = browser.get_form('post')
        form.get_control('title').value = 'Previewed comment'
        self.assertEqual(form.get_control("action.preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a message for the new comment."])

        form = browser.get_form('post')
        self.assertEqual(form.get_control('title').value, 'Previewed comment')
        form.get_control('title').value = ''
        form.get_control('text').value = 'Previewed message'
        self.assertEqual(form.get_control("action.preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new comment."])

        form = browser.get_form('post')
        self.assertEqual(form.get_control('text').value, 'Previewed message')

        # Nothing was post
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

    def test_preview_and_post(self):
        """Enter a comment, preview and post it.
        """
        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Add and preview a new comment
        self.assertTrue("Post a new comment" in browser.contents)
        form = browser.get_form('post')
        form.get_control("title").value = "New Previewed Comment"
        form.get_control("text").value = "It's about a product for forum"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        # You see the comment in the preview, and it is not posted.
        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_author, ['dummy'])
        self.assertEqual(
            browser.inspect.preview_subject,
            ['New Previewed Comment'])
        self.assertEqual(
            browser.inspect.preview_comment,
            ["It's about a product for forum"])

        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

        # Post the preview
        form = browser.get_form('post')
        self.assertEqual(
            form.get_control('title').value,
            'New Previewed Comment')
        self.assertEqual(
            form.get_control('text').value,
            "It's about a product for forum")
        self.assertEqual(form.get_control("action.post").click(), 200)

        # The comment is added and the preview is gone
        self.assertEqual(browser.inspect.feedback, ["Comment added."])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.preview_subject, [])
        self.assertEqual(browser.inspect.preview_comment, [])
        self.assertEqual(browser.inspect.subjects, ["New Previewed Comment"])
        self.assertEqual(browser.inspect.authors, ["dummy"])
        self.assertEqual(
            browser.inspect.comments,
            ["It's about a product for forum"])

    def test_preview_clear(self):
        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Add and preview a new comment
        self.assertTrue("Post a new comment" in browser.contents)
        form = browser.get_form('post')
        form.get_control("title").value = "New Previewed Comment"
        form.get_control("text").value = "It's about a product for forum"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        # Clear the preview
        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.clear").click(), 200)

        # The form is cleared
        form = browser.get_form('post')
        self.assertEqual(form.get_control("title").value, '')
        self.assertEqual(form.get_control("text").value, '')

        # The no comment is added and the preview is cleared
        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.preview_subject, [])
        self.assertEqual(browser.inspect.preview_comment, [])
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.authors, [])
        self.assertEqual(browser.inspect.comments, [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TopicFunctionalTestCase))
    return suite
