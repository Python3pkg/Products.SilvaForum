# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest

from silva.app.subscriptions.interfaces import ISubscriptionManager
from Products.SilvaForum import testing


def topic_settings(browser):
    browser.inspect.add('feedback', '//span[@class="feedback"]')
    browser.inspect.add('feedbackerror', '//span[@class="feedback warning"]')    
    browser.inspect.add(
        'title',
        '//div[@class="forum"]/h2[@class="heading"]')
    browser.inspect.add(
        'subjects',
        '//div[@class="posts"]//h5[contains(@class, "comment-heading")]')
    browser.inspect.add(
        'comments',
        '//div[@class="posts"]//div[contains(@class, "comment")]//p[@class="comment-message"]')
    browser.inspect.add(
        'authors',
        '//div[@class="posts"]//div[contains(@class, "comment")]//p[@class="author-comment"]//span[@class="author"]')
    browser.inspect.add(
        'preview_subject',
        '//div[@class="preview"]/h5[contains(@class, "comment-heading")]')
    browser.inspect.add(
        'preview_comment',
        '//div[@class="preview"]/p[contains(@class, "comment-message")]')
    browser.inspect.add(
        'preview_author',
        '//div[@class="preview"]//p[@class="author-comment"]//span[@class="username"]')


class TopicFunctionalTestCase(unittest.TestCase):
    """Functional test for Silva Forum.
    """
    layer = testing.FunctionalLayer

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
        self.assertRaises(AssertionError, form.get_control, 'subscribe')

        # You can now add a comment
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
        self.assertEqual(browser.get_link("permalink").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic/New_Comment")
        self.assertEqual(browser.get_link("Up to topic").click(), 200)
        self.assertEqual(browser.location, "/root/forum/topic")

    def test_post_as_anonymous(self):
        """Post a new comment as anonymous
        """
        testing.enable_anonymous_posting(self.root.forum)

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

        self.assertEqual(browser.get_link("permalink").click(), 200)
        self.assertEqual(
            browser.location,
            "/root/forum/topic/Anonymous_Comment")

    def test_post_preview_unauthenticated_with_captcha(self):
        """Activate unauthenicated posting and test that if you fill
        the captcha you can post unauthenticated.
        """
        testing.enable_unauthenticated_posting(self.root.forum)

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
        form.get_control("captcha").value = testing.get_captcha_word(browser)
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
        testing.enable_unauthenticated_posting(self.root.forum)

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

    def test_post_and_subscribe(self):
        """Post and subscribe to a topic.
        """
        testing.enable_subscription(self.root.forum)
        testing.set_member_email('dummy', 'dummy@example.com')

        subscriptions = ISubscriptionManager(self.root.forum.topic)
        self.assertEqual(
            subscriptions.is_subscribed('dummy@example.com'),
            False)
        self.assertEqual(len(self.root.service_mailhost.messages), 0)

        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Post a comment. We don't use a title, so the topic one is used
        form = browser.get_form('post')
        form.get_control("text").value = "How are you ?"
        self.assertEqual(form.get_control('subscribe').checked, True)
        self.assertEqual(form.get_control("action.post").click(), 200)

        # The comment is added, and the request for subscription is triggred.
        self.assertEqual(
            browser.inspect.feedback,
            ["Comment added.",
             "A confirmation mail have been sent for your subscription."])

        subscription_request = self.root.service_mailhost.read_last_message()
        self.assertNotEqual(subscription_request, None)
        self.assertEqual(subscription_request.mto, ['dummy@example.com'])
        self.assertEqual(subscription_request.mfrom, 'notification@example.com')
        self.assertEqual(
            subscription_request.subject,
            'Subscription confirmation to "Test Topic"')
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

    def test_post_notification(self):
        """Post a comment that sends a notification.
        """
        testing.enable_subscription(self.root.forum)
        testing.set_member_email('dummy', 'dummy@example.com')

        subscriptions = ISubscriptionManager(self.root.forum.topic)
        subscriptions.subscribe('dummy@example.com')

        browser = self.layer.get_browser(topic_settings)
        browser.login('dummy', 'dummy')
        self.assertEqual(browser.open('/root/forum'), 200)
        self.assertEqual(browser.get_link('Test Topic').click(), 200)

        # Post a comment. We don't use a title, so the topic one is used
        form = browser.get_form('post')
        form.get_control("title").value = "I am good"
        form.get_control("text").value = "very, very good"

        # We are already subscribed, so no option to subscribe
        self.assertRaises(AssertionError, form.get_control, 'subscribe')
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added."])

        # A mail should have been sent to dummy
        message = self.root.service_mailhost.read_last_message()
        self.assertNotEqual(message, None)
        self.assertEqual(message.content_type, 'text/plain')
        self.assertEqual(message.charset, 'utf-8')
        self.assertEqual(message.mto, ['dummy@example.com'])
        self.assertEqual(message.mfrom, 'notification@example.com')
        self.assertEqual(message.subject, 'New comment posted "I am good"')

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
            browser.inspect.feedbackerror,
            ["Please provide a message for the new comment."])

        # Noting is created
        self.assertEqual(browser.inspect.subjects, [])
        self.assertEqual(browser.inspect.comments, [])
        self.assertEqual(browser.inspect.authors, [])

        # If you provide only a message, it works. The title of the
        # topic is used by default.
        form = browser.get_form('post')
        form.get_control('text').value = 'Use default title'
        self.assertEqual(form.get_control("action.post").click(), 200)

        self.assertEqual(browser.inspect.feedback, ["Comment added."])
        self.assertEqual(browser.inspect.subjects, ['Test Topic'])
        self.assertEqual(browser.inspect.comments, ['Use default title'])
        self.assertEqual(browser.inspect.authors, ['dummy'])

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
            browser.inspect.feedbackerror,
            ["Please provide a message for the new comment."])

        form = browser.get_form('post')
        self.assertEqual(form.get_control("title").value, 'Test Topic')
        form.get_control('title').value = 'Previewed comment'
        self.assertEqual(form.get_control("action.preview").click(), 200)
        self.assertEqual(
            browser.inspect.feedbackerror,
            ["Please provide a message for the new comment."])

        form = browser.get_form('post')
        self.assertEqual(form.get_control('title').value, 'Previewed comment')

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
