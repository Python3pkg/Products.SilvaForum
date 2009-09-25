# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from Products.SilvaForum import interfaces
from Products.Silva.tests import SilvaTestCase, SilvaBrowser

from Testing.ZopeTestCase import installProduct

import urllib2

class ForumFunctionalTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Functional test for Silva Forum.
    """

    def afterSetUp(self):
        self.root.service_extensions.install('SilvaForum')
        self.forum = self.addObject(
            self.silva, 'Forum', 'forum',
            title='Test Forum', product='SilvaForum')

    def test_login_forum_and_post(self):
        """Login to post a new topic.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        self.failUnless('Test Forum' in browser.contents)

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.failIf("Post a new topic" in browser.contents)
        self.assertRaises(urllib2.HTTPError,
            browser.getControl('Login to post a new topic').click)

        silva_browser.login()
        browser = silva_browser.browser
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        # You can now add a topic
        self.failUnless("Post a new topic" in browser.contents)
        browser.getControl("Subject").value = "New Test Topic"
        browser.getControl("Add topic").click()

        # And now it's there
        self.failUnless("New Test Topic" in browser.contents)
        browser.getLink("New Test Topic").click()
        self.assertEqual(
            browser.url, "http://nohost/root/forum/New_Test_Topic")

        # And you can logout to leave.
        self.assertRaises(urllib2.HTTPError,
            browser.getControl('Logout').click)

    def test_forum_post_validation(self):
        """Try to add an empty topic.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        self.failIf("Please provide a subject" in browser.contents)

        browser.getControl("Add topic").click()

        self.failUnless("Please provide a subject" in browser.contents)

    def test_forum_preview_validation(self):
        """Try to preview an empty topic.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        self.failIf("Please provide a subject for the new topic" \
                        in browser.contents)

        browser.getControl("Preview").click()

        self.failUnless("Please provide a subject for the new topic" \
                            in browser.contents)

    def test_forum_preview_and_post(self):
        """Add a topic, preview and post it.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        # Preview a new topic
        self.failUnless("Post a new topic" in browser.contents)
        browser.getControl("Subject").value = "New Test Previewed Topic"
        browser.getControl("Preview").click()

        # Now we still have the value in the field and we post it
        self.assertEqual(browser.getControl("Subject").value,
                         "New Test Previewed Topic")
        browser.getControl("Post topic").click()

        # And it's there
        self.failUnless("New Test Previewed Topic" in browser.contents)
        browser.getLink("New Test Previewed Topic").click()
        self.assertEqual(
            browser.url, "http://nohost/root/forum/New_Test_Previewed_T")



import unittest
def test_suite():

    installProduct('SilvaForum')

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumFunctionalTestCase))
    return suite

