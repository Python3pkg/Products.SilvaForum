import unittest
from dtformat import format_dt
from datetime import datetime

class TestFormatfd(unittest.TestCase):
    def test_same_day(self):
        # test 1
        # minutes
        # control fourm variable
        fd = datetime(2007, 1, 1, 01, 00)
        
        # now
        cd = datetime(2007, 1, 1, 01, 00)
        self.assertEquals(format_dt(fd, cd), 'Just added')
        
        # minutes
        cd = datetime(2007, 1, 1, 01, 01)
        self.assertEquals(format_dt(fd, cd), '1 minute ago')
        
        cd = datetime(2007, 1, 1, 01, 02)
        self.assertEquals(format_dt(fd, cd), '2 minutes ago')

        cd = datetime(2007, 1, 1, 01, 03)
        self.assertEquals(format_dt(fd, cd), '3 minutes ago')
        
        cd = datetime(2007, 1, 1, 01, 04)
        self.assertEquals(format_dt(fd, cd), '4 minutes ago')
        
        cd = datetime(2007, 1, 1, 01, 05)
        self.assertEquals(format_dt(fd, cd), '5 minutes ago')
        
        # hours 
        cd = datetime(2007, 1, 1, 02, 00)
        self.assertEquals(format_dt(fd, cd), '1 hour ago')

        cd = datetime(2007, 1, 1, 03, 00)
        self.assertEquals(format_dt(fd, cd), '2 hours ago')

        # hours and minutes
        cd = datetime(2007, 1, 1, 02, 01)
        self.assertEquals(format_dt(fd, cd), '1 hour and 1 minute ago')

        cd = datetime(2007, 1, 1, 02, 02)
        self.assertEquals(format_dt(fd, cd), '1 hour and 2 minutes ago')

        cd = datetime(2007, 1, 1, 02, 03)
        self.assertEquals(format_dt(fd, cd), '1 hour and 3 minutes ago')

        cd = datetime(2007, 1, 1, 02, 10)
        self.assertEquals(format_dt(fd, cd), '1 hour and 10 minutes ago')

        cd = datetime(2007, 1, 1, 02, 11)
        self.assertEquals(format_dt(fd, cd), '1 hour and 11 minutes ago')

        cd = datetime(2007, 1, 1, 02, 12)
        self.assertEquals(format_dt(fd, cd), '1 hour and 12 minutes ago')

        cd = datetime(2007, 1, 1, 03, 01)
        self.assertEquals(format_dt(fd, cd), '2 hours and 1 minute ago')

        cd = datetime(2007, 1, 1, 04, 05)
        self.assertEquals(format_dt(fd, cd), '3 hours and 5 minutes ago')

        cd = datetime(2007, 1, 2, 04, 10)
        self.assertEquals(format_dt(fd, cd), '1 day, 3 hours and 10 minutes ago')

    def test_same_month(self):
        fd = datetime(2007, 1, 1, 01, 00)
        
        # days
        #cd = datetime(2007, 1, 2, 01, 00)
        #self.assertEquals(format_dt(fd, cd), '1 day ago')

        cd = datetime(2007, 1, 3, 01, 00)
        self.assertEquals(format_dt(fd, cd), '2 days ago')

        cd = datetime(2007, 1, 4, 01, 00)
        self.assertEquals(format_dt(fd, cd), '3 days ago')

        # days and hours
        cd = datetime(2007, 1, 2, 02, 00)
        self.assertEquals(format_dt(fd, cd), '1 day and 1 hour ago')

        cd = datetime(2007, 1, 3, 03, 00)
        self.assertEquals(format_dt(fd, cd), '2 days and 2 hours ago')

        # days hours and minutes
        cd = datetime(2007, 1, 2, 02, 01)
        self.assertEquals(format_dt(fd, cd), '1 day, 1 hour and 1 minute ago')

        cd = datetime(2007, 1, 3, 03, 02)
        self.assertEquals(format_dt(fd, cd), '2 days, 2 hours and 2 minutes ago')

        cd = datetime(2007, 1, 4, 04, 03)
        self.assertEquals(format_dt(fd, cd), '3 days, 3 hours and 3 minutes ago')

        # weeks
        cd = datetime(2007, 1, 8, 01, 00)
        self.assertEquals(format_dt(fd, cd), '1 week ago')
        
        cd = datetime(2007, 1, 15, 01, 00)
        self.assertEquals(format_dt(fd, cd), '2 weeks ago')

        # weeks and days
    
    def test_different_month(self):
        fd = datetime(2007, 1, 1, 1, 00)

        cd = datetime(2007, 4, 4, 15, 06)
        self.assertEquals(format_dt(fd, cd), '2007-01-01 01:00:00')

if __name__ == '__main__':
    unittest.main()

