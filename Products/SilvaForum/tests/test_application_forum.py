# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from Products.Silva.tests import SilvaTestCase, SilvaBrowser

from Testing.ZopeTestCase import installProduct

import urllib2, re

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
            browser.getControl('Login').click)

        silva_browser.login()
        browser = silva_browser.browser
        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        # You can now add a topic
        self.failUnless("Post a new topic" in browser.contents)
        browser.getControl("Subject").value = "New Test Topic"
        browser.getControl("Post topic").click()

        self.failUnless("Topic added" in browser.contents)

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

        browser.getControl("Post topic").click()

        self.failUnless("Please provide a subject" in browser.contents)

    def __activate_anonymous_post(self):
        forum = self.root.forum
        metadata = forum.service_metadata.getMetadata(forum)
        metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})

    def test_forum_post_as_anonymous(self):
        """Post a new topic as anonymous
        """
        self.__activate_anonymous_post()
        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser
        forum_url = silva_browser.get_root_url() + '/forum'

        self.assertEqual(
            silva_browser.go(forum_url),
            (200, 'http://nohost/root/forum'))

        self.failIf("Please provide a subject" in browser.contents)

        browser.getControl("Subject").value = "Anonymous post"
        browser.getControl(name="anonymous").value = '1'
        browser.getControl("Post topic").click()

        self.failUnless("Topic added" \
                        in browser.contents)

        regex = re.compile(r'<span class="author">(.*?)</span>')
        match = re.search(regex, browser.contents)
        self.failUnless(match is not None)
        author = match.group(1)
        self.assertEqual(author, 'anonymous')

    def test_forum_comment_as_anonymous(self):
        """Post a new comment as anonymous
        """
        topic = self.root.forum.manage_addProduct['SilvaForum']\
            .manage_addTopic('topic0', 'this is some topic')
        self.__activate_anonymous_post()

        silva_browser = SilvaBrowser.SilvaBrowser()
        silva_browser.login()
        browser = silva_browser.browser
        topic_url = silva_browser.get_root_url() + '/forum/topic0'

        self.assertEqual(
            silva_browser.go(topic_url),
            (200, 'http://nohost/root/forum/topic0'))

        self.failUnless("this is some topic" in browser.contents)

        browser.getControl('Subject').value = 'acomment'
        browser.getControl('Message').value = 'Comment body with some text'
        browser.getControl(name='anonymous').value = '1'
        browser.getControl('Post comment').click()

        self.failUnless("Comment added" in browser.contents)
        self.failUnless("anonymous" in browser.contents)
        browser.getLink('link').click()
        self.assertEqual(browser.url,
                         "http://nohost/root/forum/topic0/acomment")
        match = re.search(r'by<\/span>\s*(\w+)', browser.contents)
        self.failIf(match is None, "author pattern does not match anything")
        author = match.group(1)
        self.assertEqual("anonymous", author)

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
        """Enter a topic, preview and post it.
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

        self.failIf("Topic added" in browser.contents)

        # Now we still have the value in the field and we post it
        self.assertEqual(browser.getControl("Subject").value,
                         "New Test Previewed Topic")
        browser.getControl("Post topic").click()

        self.failUnless("Topic added" in browser.contents)

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

