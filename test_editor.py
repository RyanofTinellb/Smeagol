import unittest
import editor
from translation import Markdown, AddRemoveLinks, ExternalDictionary
from smeagol import Grammar

class testEditor(unittest.TestCase):
    def setUp(self):
        markdown = Markdown('c:/users/ryan/documents/tinellbianlanguages/'
                                            'grammarstoryreplacements.mkd')
        links = AddRemoveLinks([ExternalDictionary()])
        self.editor = editor.Editor(site=Grammar(), markdown=markdown,
                links=links)

    def testEditorConfiguration(self):
        expected = """#site
destination: c:/users/ryan/documents/tinellbianlanguages/grammar
name: Grammar
source: data.txt
template: template.html
main_template: main_template.html
markdown: ../replacements.mkd
searchjson: searching.json
leaf_level: 3

#editor
externaldictionary\n"""
        actual = self.editor.editor_configuration
        self.assertEqual(expected, actual,
                '\n\nExpected:\n{0}\nActual:\n{1}\n'.format(expected, actual))

    def testMakeSiteFromConfig(self):
        config_filename = ('c:/users/ryan/documents/tinellbianlanguages/'
                            'smeagol/makesitefromconfig.txt')
        with open(config_filename) as config_file:
            config = config_file.read()
        site = self.editor.make_site_from_config(config)
        self.assertEqual(site.name, 'Ryan', 'Site {0} not created correctly'.format(site.name))
        self.assertEqual(site.destination, 'c:/users/ryan/desktop',
                'Site mistakenly placed at {0}'.format(site.destination))

    def testGetLinkAdderFromConfig(self):
        config_filename = ('c:/users/ryan/documents/tinellbianlanguages/'
                            'smeagol/getlinkadderfromconfig.txt')
        with open(config_filename) as config_file:
            config = config_file.read()
            links = self.editor.get_linkadder_from_config(config)
            expected = {'externaldictionary': '', 'externalgrammar':
                    'c:/users/ryan/documents/tinellbianlanguages/dictionarylinks.txt'}
            self.assertEqual(expected, links.details)


if __name__ == '__main__':
    unittest.main()
