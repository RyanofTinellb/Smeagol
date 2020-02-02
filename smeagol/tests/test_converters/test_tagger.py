from ...conversion import Tagger
import pytest

@pytest.fixture
def tagger():
    return Tagger('''{"transliteration": {"key": "b", "tags": ["<span class=\\\"transliteration\\\">", "</span>" ], "bold": true, "language": true, "background": "green", "group": "paragraph" }, "definition": {"key": "i", "tags": ["<span class=\\\"definition\\\">", "</span>" ], "italics": true}, "glossary": {"key": "k", "tags": ["<span class=\\\"glossary\\\">", "</span>" ], "font": "Alegreya SC" }, "link": {"key": "n", "underline": true, "colour": "blue", "hyperlink": true, "language": true}, "broken-link": {"underline": true, "colour": "red", "hyperlink": true}, "tinellbian": {"tags": ["<span class=\\\"script\\\">", "</span>" ], "font": "Tinellbian", "language": true}, "pronunciation": {"key": "I", "tags": ["<span class=\\\"pronunciation\\\">", "</span>" ], "font": "Lucida Sans Unicode" }, "highlight": {"key": "H", "tags": ["<strong>", "</strong" ], "colour": "red" }}''')

def test_tagger(tagger):
    assert tagger.names == ['default', 'transliteration', 'definition', 'glossary', 'link', 'broken-link', 'tinellbian', 'pronunciation', 'highlight']

def test_copy(tagger):
    copy = tagger.copy()
    assert type(copy) == Tagger
    assert copy.names == tagger.names
    tagger['transliteration'].bold = False
    assert copy['transliteration'].bold

def test_remove(tagger):
    tagger.remove('transliteration')
    assert tagger.names == ['default', 'definition', 'glossary', 'link', 'broken-link', 'tinellbian', 'pronunciation', 'highlight']
    tagger.remove(tagger['glossary'])
    assert tagger.names == ['default', 'definition', 'link', 'broken-link', 'tinellbian', 'pronunciation', 'highlight']