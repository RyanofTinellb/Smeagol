from smeagol import Grammar
import unittest

class TestHyperlinks(unittest.TestCase):

    k =  Grammar()

    def test_hyperlinks(self):
        k = TestHyperlinks.k
        for f, g, h, i in [
            ('Phonology', 'Consonants',
                    'consonants.html', 'index.html'),
            ('High Lulani', 'Consonants',
                    'phonology/consonants.html', '../index.html'),
            ('High Lulani', 'Phonology',
                    'phonology/index.html', '../index.html'),
            ('Grammar', 'High Lulani',
                    'highlulani/index.html', '../index.html'),
            ('Grammar', 'Consonants',
                    'highlulani/phonology/consonants.html',
                    '../../index.html'),
            ('Phonology', 'Morphology',
                '../morphology/index.html', '../phonology/index.html'),
            ('Phonology', 'Nouns',
                '../morphology/nouns.html', '../phonology/index.html'),
            ('Introduction', 'Morphology',
                '../highlulani/morphology/index.html', '../../introduction/index.html'),
            ('Introduction', 'Nouns',
                '../highlulani/morphology/nouns.html', '../../introduction/index.html')
            ]:
                l = k[f].hyperlink(k[g], anchors=False)
                m = k[g].hyperlink(k[f], anchors=False)
                self.assertEqual(l, h, '{0} -> {1}: {2} <> {3}'.format(
                    f, g, l, h))
                self.assertEqual(m, i, '{0} -> {1}: {2} <> {3}'.format(
                    g, f, m, i))

# if __name__ == '__main__':
unittest.main()
