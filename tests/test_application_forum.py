# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest

from zope.component import getUtility

from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaForum.testing import FunctionalLayer


def forum_settings(browser):
    browser.inspect.add('feedback', '//div[@class="feedback"]/span')
    browser.inspect.add('title', '//div[@class="forum"]/descendant::h2')
    browser.inspect.add(
        'topics',
        '//table[@class="forum-content-table"]//td[@class="topic"]/p/a',
        type='link')
    browser.inspect.add(
        'authors',
        '//table[@class="forum-content-table"]//td[@class="poster"]/p')
    browser.inspect.add(
        'preview_topic',
        '//table[@class="forum-content-preview"]//td[@class="topic"]/p')
    browser.inspect.add(
        'preview_author',
        '//table[@class="forum-content-preview"]//td[@class="author"]/p')


class ForumFunctionalTestCase(unittest.TestCase):
    """Functional test for Silva Forum.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaForum']
        factory.manage_addForum('forum', 'Test Forum')

    def test_login_and_post(self):
        """Login to post a new topic.
        """
        browser = self.layer.get_browser(forum_settings)

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.title, ['Test Forum'])

        # By default the forum is empty
        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.assertFalse("Post a new topic" in browser.contents)
        self.assertRaises(AssertionError, browser.get_form, 'post')
        browser.login('dummy', 'dummy')
        browser.reload()

        # You can now add a topic
        self.assertTrue("Post a new topic" in browser.contents)
        form = browser.get_form('post')
        form.get_control("topic").value = "New Test Topic"
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])

        # The form is cleared after
        form = browser.get_form('post')
        self.assertEqual(form.get_control("topic").value, '')

        self.assertEqual(browser.inspect.topics, ["New Test Topic"])
        self.assertEqual(browser.inspect.authors, ['dummy'])

        self.assertEqual(browser.inspect.topics["New Test Topic"].click(), 200)
        self.assertEqual(browser.location, "/root/forum/New_Test_Topic")

    def test_post_validation(self):
        """Try to add an empty topic.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)

        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.post").click(), 200)

        # Error reporting nothing posted
        self.assertEqual(browser.inspect.feedback, ["Please provide a subject"])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

    def test_post_and_preview_as_anonymous(self):
        """Post a new topic as anonymous
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        form = browser.get_form('post')
        form.get_control("topic").value = "Anonymous post"
        self.assertEqual(form.get_control("anonymous").checked, False)
        form.get_control("anonymous").checked = True
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_topic, ["Anonymous post"])
        self.assertEqual(browser.inspect.preview_author, ['anonymous'])

        form = browser.get_form('post')
        self.assertEqual(form.get_control("topic").value, "Anonymous post")
        self.assertEqual(form.get_control("anonymous").checked, True)
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, ["Anonymous post"])
        self.assertEqual(browser.inspect.authors, ['anonymous'])

        self.assertEqual(browser.inspect.topics["Anonymous post"].click(), 200)
        self.assertEqual(browser.location, '/root/forum/Anonymous_post')

    def test_preview_validation(self):
        """Try to preview an empty topic.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)

        form = browser.get_form('post')
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new topic"])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

    def test_preview_and_post(self):
        """Enter a topic, preview and post it.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        # Preview a new topic
        form = browser.get_form('post')
        form.get_control("topic").value = "Previewed Topic"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_topic, ['Previewed Topic'])
        self.assertEqual(browser.inspect.preview_author, ['dummy'])

        # Nothing is created, it is still a preview
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

        # Now we still have the value in the field and we post it
        form = browser.get_form('post')
        self.assertEqual(form.get_control('topic').value, "Previewed Topic")
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])

        # And it's there
        self.assertEqual(browser.inspect.topics, ["Previewed Topic"])
        self.assertEqual(browser.inspect.authors, ["dummy"])

        self.assertEqual(browser.inspect.topics["Previewed Topic"].click(), 200)
        self.assertEqual(browser.location, "/root/forum/Previewed_Topic")

    def test_preview_clear(self):
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        # Preview a new topic
        form = browser.get_form('post')
        form.get_control("topic").value = "Previewed Topic"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        # Now we still have the value in the field and we post it
        form = browser.get_form('post')
        self.assertEqual(form.get_control('topic').value, "Previewed Topic")
        self.assertEqual(form.get_control("action.clear").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])

        form = browser.get_form('post')
        self.assertEqual(form.get_control('topic').value, "")

        # No topic have been created
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumFunctionalTestCase))
    return suite
