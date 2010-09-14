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
    browser.inspect.add('title', '//div[@id="content"]/descendant::h2')
    browser.inspect.add('author', '//td[@class="poster"]/p')


class ForumFunctionalTestCase(unittest.TestCase):
    """Functional test for Silva Forum.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaForum']
        factory.manage_addForum('forum', 'Test Forum')

    def test_login_forum_and_post(self):
        """Login to post a new topic.
        """
        browser = self.layer.get_browser(forum_settings)

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.title, ['Test Forum'])

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.assertFalse("Post a new topic" in browser.contents)
        browser.login('dummy', 'dummy')
        browser.reload()

        # You can now add a topic
        self.assertTrue("Post a new topic" in browser.contents)
        form = browser.get_form('posttopic')
        form.get_control("topic").value = "New Test Topic"
        self.assertEqual(form.get_control("submit").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])
        self.assertEqual(browser.inspect.author, ['dummy'])

        self.assertTrue("New Test Topic" in browser.contents)
        browser.get_link("New Test Topic").click()
        self.assertEqual(browser.location, "/root/forum/New_Test_Topic")

    def test_forum_post_validation(self):
        """Try to add an empty topic.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.feedback, [])

        form = browser.get_form('posttopic')
        self.assertEqual(form.get_control("submit").click(), 200)
        self.assertEqual(browser.inspect.feedback, ["Please provide a subject"])

    def test_forum_post_as_anonymous(self):
        """Post a new topic as anonymous
        """
        metadata = getUtility(IMetadataService).getMetadata(self.root.forum)
        metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        form = browser.get_form('posttopic')
        form.get_control("topic").value = "Anonymous post"
        form.get_control("anonymous").checked = True
        self.assertEqual(form.get_control("submit").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])
        self.assertEqual(browser.inspect.author, ['anonymous'])

    def test_forum_preview_validation(self):
        """Try to preview an empty topic.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.feedback, [])

        form = browser.get_form('posttopic')
        self.assertEqual(form.get_control("preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new topic"])

    def test_forum_preview_and_post(self):
        """Enter a topic, preview and post it.
        """
        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')

        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.inspect.feedback, [])

        # Preview a new topic
        form = browser.get_form('posttopic')
        form.get_control("topic").value = "Previewed Topic"
        self.assertEqual(form.get_control("preview").click(), 200)
        self.assertEqual(browser.inspect.feedback, [])

        # Now we still have the value in the field and we post it
        form = browser.get_form('posttopic')
        self.assertEqual(form.get_control('topic').value, "Previewed Topic")
        form = browser.get_form('previewform')
        self.assertEqual(form.get_control('topic').value, "Previewed Topic")
        self.assertEqual(form.get_control("submit").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added"])

        # And it's there
        self.assertTrue("Previewed Topic" in browser.contents)
        browser.get_link("Previewed Topic").click()
        self.assertEqual(browser.location, "/root/forum/Previewed_Topic")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumFunctionalTestCase))
    return suite
