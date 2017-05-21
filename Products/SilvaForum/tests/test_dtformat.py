# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# See also LICENSES.txt

import unittest
from Products.SilvaForum.dtformat import dtformat
from datetime import datetime


class TestFormatDT(unittest.TestCase):

    def test_same_day(self):
        fd = datetime(2007, 1, 1, 0o1, 00)
        cd = datetime(2007, 1, 1, 0o1, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Just added')

        # minutes
        cd = datetime(2007, 1, 1, 0o1, 0o1)
        self.assertEquals(dtformat(None, fd, cd), 'Added one minute ago')

        cd = datetime(2007, 1, 1, 0o1, 0o2)
        self.assertEquals(dtformat(None, fd, cd), 'Added 2 minutes ago')

        cd = datetime(2007, 1, 1, 0o1, 0o3)
        self.assertEquals(dtformat(None, fd, cd), 'Added 3 minutes ago')

        cd = datetime(2007, 1, 1, 0o1, 0o4)
        self.assertEquals(dtformat(None, fd, cd), 'Added 4 minutes ago')

        cd = datetime(2007, 1, 1, 0o1, 0o5)
        self.assertEquals(dtformat(None, fd, cd), 'Added 5 minutes ago')

        # hours
        cd = datetime(2007, 1, 1, 0o2, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added one hour ago')

        cd = datetime(2007, 1, 1, 0o3, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added 2 hours ago')

        # hours and minutes
        cd = datetime(2007, 1, 1, 0o2, 0o1)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, one minute ago')

        cd = datetime(2007, 1, 1, 0o2, 0o2)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, 2 minutes ago')

        cd = datetime(2007, 1, 1, 0o2, 0o3)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, 3 minutes ago')

        cd = datetime(2007, 1, 1, 0o2, 10)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, 10 minutes ago')

        cd = datetime(2007, 1, 1, 0o2, 11)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, 11 minutes ago')

        cd = datetime(2007, 1, 1, 0o2, 12)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one hour, 12 minutes ago')

        cd = datetime(2007, 1, 1, 0o3, 0o1)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added 2 hours, one minute ago')

        cd = datetime(2007, 1, 1, 0o4, 0o5)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added 3 hours, 5 minutes ago')

        cd = datetime(2007, 1, 2, 0o4, 10)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one day, 3 hours ago')

    def test_same_month(self):
        fd = datetime(2007, 1, 1, 0o1, 00)
        cd = datetime(2007, 1, 3, 0o1, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added 2 days ago')

        cd = datetime(2007, 1, 4, 0o1, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added 3 days ago')

        # days and hours
        cd = datetime(2007, 1, 2, 0o2, 00)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one day, one hour ago')

        cd = datetime(2007, 1, 3, 0o3, 00)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added 2 days, 2 hours ago')

        # days hours, minutes
        cd = datetime(2007, 1, 2, 0o2, 0o1)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one day, one hour ago')

        cd = datetime(2007, 1, 3, 0o3, 0o2)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added 2 days, 2 hours ago')

        cd = datetime(2007, 1, 4, 0o4, 0o3)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added 3 days, 3 hours ago')

        # weeks
        cd = datetime(2007, 1, 8, 0o1, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added one week ago')

        cd = datetime(2007, 1, 15, 0o1, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Added 2 weeks ago')

    def test_different_month(self):
        fd = datetime(2007, 1, 1, 1, 00)
        cd = datetime(2007, 4, 4, 15, 0o6)
        self.assertEquals(dtformat(None, fd, cd), '2007-01-01 01:00:00')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormatDT))
    return suite
