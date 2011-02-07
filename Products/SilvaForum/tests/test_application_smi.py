# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.SilvaForum.testing import FunctionalLayer
from Products.Silva.testing import smi_settings


class SMIFunctionalTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_add(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('editor', 'editor')
        self.assertEqual(browser.open('/root/edit'), 200)

        # Create a forum
        browser.macros.create('Silva Forum', id='forum', title='Forum')
        self.assertEqual(browser.inspect.folder_listing, ['index', 'forum'])
        self.assertEqual(browser.inspect.folder_listing['forum'].click(), 200)
        self.assertEqual(browser.location, '/root/forum/edit/tab_edit')
        self.assertEqual(
            browser.inspect.tabs,
            ['contents', 'preview', 'properties', 'publish'])

        # Create a topic inside the forum
        browser.macros.create('Silva Forum Topic', id='topic', title='Topic')
        self.assertEqual(browser.inspect.folder_listing, ['topic'])
        self.assertEqual(browser.inspect.folder_listing['topic'].click(), 200)
        self.assertEqual(browser.location, '/root/forum/topic/edit/tab_edit')
        self.assertEqual(
            browser.inspect.tabs,
            ['contents', 'preview', 'properties', 'publish'])

        self.assertEqual(self.root.forum.number_of_topics(), 1)

        # Create a comment in the topic
        browser.macros.create(
            'Silva Forum Comment',
            id='com', title='Comment', text='Comment text')
        self.assertEqual(browser.inspect.folder_listing, ['com'])
        self.assertEqual(browser.inspect.folder_listing['com'].click(), 200)
        self.assertEqual(
            browser.location,
            '/root/forum/topic/com/edit/tab_edit')
        self.assertEqual(
            browser.inspect.tabs,
            ['edit', 'preview', 'properties'])

        # Edit the comment
        form = browser.get_form('editform')
        self.assertEqual(
            form.get_control('editform.field.text').value,
            'Comment text')
        form.get_control('editform.field.text').value = u'New comment text'
        self.assertEqual(
            form.get_control('editform.action.save-changes').click(),
            200)
        self.assertEqual(
            browser.inspect.feedback, ['Changes saved.'])

        self.assertEqual(self.root.forum.topic.number_of_comments(), 1)
        self.assertEqual(
            self.root.forum.topic.com.get_text(),
            u"New comment text")

        # Delete the forum
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        self.assertTrue('forum' in browser.inspect.folder_listing)
        browser.macros.delete('forum')
        self.assertFalse('forum' in browser.inspect.folder_listing)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SMIFunctionalTestCase))
    return suite
