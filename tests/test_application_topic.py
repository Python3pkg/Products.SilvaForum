# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from Products.Silva.tests import SilvaTestCase, SilvaBrowser

from Testing.ZopeTestCase import installProduct

import urllib2


class TopicFunctionalTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Functional test for Silva Forum.
    """

    def afterSetUp(self):
        self.root.service_extensions.install('SilvaForum')
        self.forum = self.addObject(
            self.silva, 'Forum', 'forum',
            title='Test Forum', product='SilvaForum')
        self.topic = self.addObject(
            self.forum, 'Topic', 'Test_Topic',
            title='Test Topic', product='SilvaForum')

    def test_login_and_post_comment(self):
        """Login to post a new comment in a topic.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        self.failUnless('Test Forum' in browser.contents)
        browser.getLink('Test Topic').click()

        # You need to login to post something. The login button
        # actually raise a 401 so you have a browser login.
        self.failIf("Post a new comment" in browser.contents)
        self.assertRaises(urllib2.HTTPError,
            browser.getControl('Login').click)

        silva_browser.login()
        browser = silva_browser.browser
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))
        browser.getLink('Test Topic').click()

        # You can now add a topic
        self.failUnless("Post a new comment" in browser.contents)
        browser.getControl("Subject").value = "New Comment"
        browser.getControl("Message").value = "It's about a product for forum"
        browser.getControl("Post comment").click()

        self.failUnless("Comment added" in browser.contents)

        # And now it's there
        self.failUnless("New Comment" in browser.contents)
        self.failUnless("It's about a product for forum" in browser.contents)

        browser.getLink("posted").click()
        self.assertEqual(
            browser.url,
            "http://nohost/root/forum/Test_Topic/New_Comment")
        browser.getLink("Up to topic...").click()
        self.assertEqual(
            browser.url,
            "http://nohost/root/forum/Test_Topic")

        # And you can logout to leave.
        self.assertRaises(urllib2.HTTPError,
            browser.getControl('Logout').click)

    def test_topic_post_validation(self):
        """Try to add an empty comment.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))
        browser.getLink('Test Topic').click()

        self.failIf(
            "Please provide a message for the new comment" in browser.contents)

        browser.getControl("Post comment").click()

        self.failUnless(
            "Please provide a message for the new comment" in browser.contents)

    def test_post_topic_as_anonymous(self):
        """Try to post a new topic as anonymous
        """

        silva_browser = SilvaBrowser.SilvaBrowser()
        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))



    def test_topic_preview_validation(self):
        """Try to preview an empty or incomplete comment.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))
        browser.getLink('Test Topic').click()

        self.failIf("Please provide a message for the new comment" \
                        in browser.contents)

        browser.getControl('Preview').click()

        self.failUnless("Please provide a message for the new comment" \
                        in browser.contents)

        self.assertEqual(browser.getControl('Subject').value, 'Test Topic')
        browser.getControl('Subject').value = 'New previewed comment'
        browser.getControl('Preview').click()

        self.failUnless("Please provide a message for the new comment" \
                        in browser.contents)
        self.assertEqual(
            browser.getControl('Subject').value,
            'New previewed comment')

        browser.getControl('Subject').value = ''
        browser.getControl('Message').value = 'New previewed message'
        browser.getControl('Preview').click()

        self.failIf("Please provide a message for the new comment" \
                        in browser.contents)
        self.assertEqual(
            browser.getControl('Message').value,
            'New previewed message')

    def test_comment_preview_and_post(self):
        """Enter a comment, preview and post it.
        """
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser

        forum_url = silva_browser.get_root_url() + '/forum'
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))
        browser.getLink('Test Topic').click()

        # Add and preview a new comment
        self.failUnless("Post a new comment" in browser.contents)
        browser.getControl("Subject").value = "New Previewed Comment"
        browser.getControl("Message").value = "It's about a product for forum"
        browser.getControl("Preview").click()

        self.failIf("Comment added" in browser.contents)

        browser.getControl("Post comment", index=0).click()

        self.failUnless("Comment added" in browser.contents)
        self.failUnless("New Previewed Comment" in browser.contents)
        self.failUnless("It's about a product for forum" in browser.contents)



import unittest
def test_suite():

    installProduct('SilvaForum')

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TopicFunctionalTestCase))
    return suite

