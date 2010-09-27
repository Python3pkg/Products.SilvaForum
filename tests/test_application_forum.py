# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest

from Products.SilvaForum import testing
from silva.app.subscriptions.interfaces import ISubscriptionManager


def forum_settings(browser):
    browser.inspect.add('feedback', '//div[contains(@class, "feedback")]/span')
    browser.inspect.add('title', '//div[@class="forum"]//h2')
    browser.inspect.add(
        'topics',
        '//table[@class="forum-content-table"]//td[@class="topic"]/p/a',
        type='link')
    browser.inspect.add(
        'authors',
        '//table[@class="forum-content-table"]//td[@class="poster"]/p')
    browser.inspect.add(
        'preview_topic',
        '//table[contains(@class,"forum-preview")]//td[@class="topic"]/p')
    browser.inspect.add(
        'preview_author',
        '//table[contains(@class,"forum-preview")]//td[@class="author"]/p')



class ForumFunctionalTestCase(unittest.TestCase):
    """Functional test for Silva Forum.
    """
    layer = testing.FunctionalLayer

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

        # By default you have no captcha or anonymous options
        self.assertRaises(AssertionError, form.get_control, 'captcha')
        self.assertRaises(AssertionError, form.get_control, 'anonymous')
        self.assertRaises(AssertionError, form.get_control, 'subscribe')

        form.get_control("topic").value = "New Test Topic"
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added."])

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
        self.assertEqual(
            browser.inspect.feedback,
            ["Please provide a subject for the new topic."])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

    def test_post_and_preview_as_anonymous(self):
        """Post a new topic as anonymous
        """
        testing.enable_anonymous_posting(self.root.forum)

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

        self.assertEqual(browser.inspect.feedback, ["Topic added."])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, ["Anonymous post"])
        self.assertEqual(browser.inspect.authors, ['anonymous'])

        self.assertEqual(browser.inspect.topics["Anonymous post"].click(), 200)
        self.assertEqual(browser.location, '/root/forum/Anonymous_post')

    def test_post_preview_unauthenticated_with_captcha(self):
        """Activate unauthenicated posting and test the captcha
        integration.
        """
        testing.enable_unauthenticated_posting(self.root.forum)

        browser = self.layer.get_browser(forum_settings)
        self.assertEqual(browser.open('/root/forum'), 200)

        # We are not authenticated, but the form to post is here
        self.assertTrue("Post a new topic" in browser.contents)
        form = browser.get_form('post')

        # The anonymous options is not here, even if it selected, are
        # we already are anonymous
        self.assertRaises(AssertionError, form.get_control, 'anonymous')

        form.get_control("topic").value = "Hello world"
        self.assertEqual(form.get_control("action.preview").click(), 200)

        self.assertEqual(browser.inspect.feedback, [])
        self.assertEqual(browser.inspect.preview_topic, ["Hello world"])
        self.assertEqual(browser.inspect.preview_author, ['anonymous'])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

        # Try to post
        form = browser.get_form('post')
        self.assertEqual(form.get_control("topic").value, "Hello world")
        self.assertEqual(form.get_control("action.post").click(), 200)

        # We didn't fill the captcha, the post was not commited
        self.assertEqual(browser.inspect.feedback, ["Invalid captcha value"])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, [])
        self.assertEqual(browser.inspect.authors, [])

        # Try to post filling the captcha
        form = browser.get_form('post')
        form.get_control("captcha").value = testing.get_captcha_word(browser)
        self.assertEqual(form.get_control("topic").value, "Hello world")
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added."])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, ['Hello world'])
        self.assertEqual(browser.inspect.authors, ['anonymous'])

    def test_post_authenticated_with_captcha(self):
        """Activate unauthenicated posting and test that you have no
        captcha for authenticated users.
        """
        testing.enable_unauthenticated_posting(self.root.forum)

        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        # We are not authenticated, but the form to post is here
        self.assertTrue("Post a new topic" in browser.contents)
        form = browser.get_form('post')

        # The captcha options is not here as we are already authenticated
        self.assertRaises(AssertionError, form.get_control, 'captcha')

        form.get_control("topic").value = "Hello forum"
        self.assertEqual(form.get_control("anonymous").checked, False)
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Topic added."])
        self.assertEqual(browser.inspect.preview_topic, [])
        self.assertEqual(browser.inspect.preview_author, [])
        self.assertEqual(browser.inspect.topics, ['Hello forum'])
        self.assertEqual(browser.inspect.authors, ['dummy'])

    def test_post_and_subscribe(self):
        """Test posting and subscribing to a topic.
        """
        testing.enable_subscription(self.root.forum)
        testing.set_member_email('dummy', 'dummy@example.com')

        self.assertEqual(len(self.root.service_mailhost.messages), 0)

        browser = self.layer.get_browser(forum_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)

        form = browser.get_form('post')
        form.get_control("topic").value = "topic"
        self.assertEqual(form.get_control("subscribe").checked, True)
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(
            browser.inspect.feedback,
            ["Topic added.",
             "A confirmation mail have been sent for your subscription."])

        subscriptions = ISubscriptionManager(self.root.forum.topic)
        self.assertEqual(subscriptions.is_subscribable(), True)

        subscription_request = self.root.service_mailhost.read_last_message()
        self.assertNotEqual(subscription_request, None)
        self.assertEqual(subscription_request.mto, ['dummy@example.com'])
        self.assertEqual(subscription_request.mfrom, 'notification@example.com')
        self.assertEqual(
            subscription_request.subject,
            'Subscription confirmation to "topic"')
        self.assertEqual(len(subscription_request.urls), 2)

        # the confirmation link is the last url in the mail
        confirmation_url = subscription_request.urls[-1]
        self.assertEqual(browser.open(confirmation_url), 200)
        self.assertEqual(
            browser.location,
            '/root/forum/topic/subscriptions.html/@@confirm_subscription')
        self.assertEqual(
            browser.html.xpath('//p[@class="subscription-result"]/text()'),
            ['You have been successfully subscribed. '
             'You will now receive email notifications.'])

        self.assertEqual(subscriptions.is_subscribed('dummy@example.com'), True)

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
            ["Please provide a subject for the new topic."])
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

        self.assertEqual(browser.inspect.feedback, ["Topic added."])
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
