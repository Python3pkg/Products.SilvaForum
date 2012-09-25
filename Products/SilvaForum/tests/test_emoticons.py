# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# See also LICENSES.txt

import unittest

from Products.SilvaForum.emoticons import emoticons, flatten_smileydata


class EmoticonsTestCase(unittest.TestCase):

    def test_no_emoticons(self):
        self.assertEquals(
            'foo', emoticons('foo', ''))
        self.assertEquals(
            'foo(bar:b)az-)',
            emoticons('foo(bar:b)az-)', ''))

    def test_simple_smiley(self):
        self.assertEquals(
            '<img src="/happy.gif" alt=": )" />',
            emoticons(':)', ''))

    def test_double_smiley(self):
        self.assertEquals(
            '<img src="/happy.gif" alt=": )" />'
            '<img src="/wink.gif" alt="; )" />',
            emoticons(':-);)', ''))

    def test_some_chars(self):
        self.assertEquals('):-,<:', emoticons('):-,<:', ''))

    def test_imagedir(self):
        self.assertEquals(
            '<img src="/foo/happy.gif" alt=": )" />',
            emoticons(':)', '/foo'))
        self.assertEquals(
            '<img src="/foo/happy.gif" alt=": )" />',
            emoticons(':)', '/foo/'))

    def test_flatten_smileydata(self):
        input = {'angry.gif': (':x', ': x'),
                 'happy.gif': (':)', ': )'),
                }
        expected = [('angry.gif', ':x'), ('angry.gif', ': x'),
                    ('happy.gif', ':)'), ('happy.gif', ': )')]
        expected.sort()
        output = flatten_smileydata(input)
        output.sort()
        self.assertEquals(expected, output)

        self.assertEquals(
            flatten_smileydata({'foo.gif': (':)', ':- )', ':-)')}),
            [('foo.gif', ':- )'), ('foo.gif', ':-)'), ('foo.gif', ':)')])

    def test_double_replace(self):
        self.assertEquals(
            emoticons('some text :oops:', ''),
            'some text <img src="/embarrassment.gif" alt=":oops:" />')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EmoticonsTestCase))
    return suite
