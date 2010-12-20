import unittest
from emoticons import emoticons, flatten_smileydata

class TestEmoticons(unittest.TestCase):
    def setUp(self):
        self.imagedir = ''

    def test_no_emoticons(self):
        self.assertEquals('foo', emoticons('foo', self.imagedir))
        self.assertEquals('foo(bar:b)az-)',
                           emoticons('foo(bar:b)az-)', self.imagedir))

    def test_simple_smiley(self):
        self.assertEquals('<img src="/happy.gif" alt=": )" />',
                          emoticons(':)', self.imagedir))

    def test_double_smiley(self):
        self.assertEquals('<img src="/happy.gif" alt=": )" /><img src="/wink.gif" alt="; )" />',
                          emoticons(':-);)', self.imagedir))

    def test_some_chars(self):
        self.assertEquals('):-,<:', emoticons('):-,<:', self.imagedir))

    def test_imagedir(self):
        self.assertEquals('<img src="/foo/happy.gif" alt=": )" />',
                          emoticons(':)', '/foo'))
        self.assertEquals('<img src="/foo/happy.gif" alt=": )" />',
                          emoticons(':)', '/foo/'))

    def test_length(self):
        pass
        # test checking emoticon length
        # test that longest emoticons is processed first

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

        input = {'foo.gif': (':)', ':- )', ':-)')}
        expected = [('foo.gif', ':- )'), ('foo.gif', ':-)'), ('foo.gif', ':)')]
        output = flatten_smileydata(input)
        self.assertEquals(expected, output)

    def test_double_replace(self):
        input = 'some text :oops:'
        expected = 'some text <img src="/embarrassment.gif" alt=":oops:" />'
        output = emoticons(input, self.imagedir)
        self.assertEquals(expected, output)

if __name__ == '__main__':
    unittest.main()

