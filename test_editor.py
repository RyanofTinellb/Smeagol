import unittest
import editor
from translation import Markdown, AddRemoveLinks, ExternalDictionary
from smeagol import Grammar

class testEditorConfiguration(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
