# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

import unittest
from Products.SilvaForum.dtformat import dtformat
from datetime import datetime


class TestFormatDT(unittest.TestCase):

    def test_same_day(self):
        fd = datetime(2007, 1, 1, 01, 00)
        cd = datetime(2007, 1, 1, 01, 00)
        self.assertEquals(dtformat(None, fd, cd), 'Just added')

        # minutes
        cd = datetime(2007, 1, 1, 01, 01)
        self.assertEquals(dtformat(None, fd, cd), u'Added one minute ago')

        cd = datetime(2007, 1, 1, 01, 02)
        self.assertEquals(dtformat(None, fd, cd), u'Added 2 minutes ago')

        cd = datetime(2007, 1, 1, 01, 03)
        self.assertEquals(dtformat(None, fd, cd), u'Added 3 minutes ago')

        cd = datetime(2007, 1, 1, 01, 04)
        self.assertEquals(dtformat(None, fd, cd), u'Added 4 minutes ago')

        cd = datetime(2007, 1, 1, 01, 05)
        self.assertEquals(dtformat(None, fd, cd), u'Added 5 minutes ago')

        # hours
        cd = datetime(2007, 1, 1, 02, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added one hour ago')

        cd = datetime(2007, 1, 1, 03, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added 2 hours ago')

        # hours and minutes
        cd = datetime(2007, 1, 1, 02, 01)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, one minute ago')

        cd = datetime(2007, 1, 1, 02, 02)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, 2 minutes ago')

        cd = datetime(2007, 1, 1, 02, 03)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, 3 minutes ago')

        cd = datetime(2007, 1, 1, 02, 10)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, 10 minutes ago')

        cd = datetime(2007, 1, 1, 02, 11)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, 11 minutes ago')

        cd = datetime(2007, 1, 1, 02, 12)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one hour, 12 minutes ago')

        cd = datetime(2007, 1, 1, 03, 01)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added 2 hours, one minute ago')

        cd = datetime(2007, 1, 1, 04, 05)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added 3 hours, 5 minutes ago')

        cd = datetime(2007, 1, 2, 04, 10)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one day, 3 hours ago')

    def test_same_month(self):
        fd = datetime(2007, 1, 1, 01, 00)
        cd = datetime(2007, 1, 3, 01, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added 2 days ago')

        cd = datetime(2007, 1, 4, 01, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added 3 days ago')

        # days and hours
        cd = datetime(2007, 1, 2, 02, 00)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added one day, one hour ago')

        cd = datetime(2007, 1, 3, 03, 00)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added 2 days, 2 hours ago')

        # days hours, minutes
        cd = datetime(2007, 1, 2, 02, 01)
        self.assertEquals(
            dtformat(None, fd, cd),
            'Added one day, one hour ago')

        cd = datetime(2007, 1, 3, 03, 02)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added 2 days, 2 hours ago')

        cd = datetime(2007, 1, 4, 04, 03)
        self.assertEquals(
            dtformat(None, fd, cd),
            u'Added 3 days, 3 hours ago')

        # weeks
        cd = datetime(2007, 1, 8, 01, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added one week ago')

        cd = datetime(2007, 1, 15, 01, 00)
        self.assertEquals(dtformat(None, fd, cd), u'Added 2 weeks ago')

    def test_different_month(self):
        fd = datetime(2007, 1, 1, 1, 00)
        cd = datetime(2007, 4, 4, 15, 06)
        self.assertEquals(dtformat(None, fd, cd), u'2007-01-01 01:00:00')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormatDT))
    return suite


