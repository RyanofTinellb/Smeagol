from smeagol import *
from random import shuffle
from translation import Markdown
import unittest

class TestOrdering(unittest.TestCase):
    def setUp(self):
        self.root = Page('')
        self.markdown = Markdown('c:/users/ryan/documents/tinellbianlanguages/replacements.mkd')
        with open('c:/users/ryan/documents/tinellbianlanguages/smeagol/proper_order.txt') as calibration:
            self.proper_order = calibration.read().splitlines()
            for element in self.proper_order:
                page = Page(name=element, parent=self.root, markdown=self.markdown)
                page.insert()
                self.root.children.reverse()
                self.root.children.sort()

    def testTinellbianAlphabet(self):
        actual = [child.name for child in self.root.children]
        debug = debug_info(self.proper_order, actual)
        self.assertEqual(self.proper_order, actual, 'These are out of order:\n' + debug)

def debug_info(*args):
    debug = ''
    try:
        for expected, actual in zip(*args):
            if expected != actual:
                scores = map(lambda x: Page(x).flatname.score, (expected, actual))
                debug += '{0}: {2} / {1}: {3}\n'.format(expected, actual, *scores)
    except AttributeError:
        raise AttributeError('Only supply two lists')
    return debug

if __name__ == '__main__':
    unittest.main(verbosity=2)
