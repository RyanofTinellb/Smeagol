import os
import pytest
from ...conversion import Markdown
from smeagol import utils

@pytest.fixture
def markdown_text():
    return [
        {
            "markup": "é",
            "markdown": "(e",
            "display_markdown": False
        },
        {
            "markup": "animate noun",
            "markdown": "*kinship*",
            "display_markdown": True
        }
    ]

@pytest.fixture
def file_markdown(markdown_text):
    folder = os.getenv('LOCALAPPDATA')
    filename = os.path.join(folder, 'smeagol_test.json')
    utils.save(markdown_text, filename)
    yield Markdown(filename)
    os.remove(filename)

@pytest.fixture
def markdown(markdown_text):
    return Markdown(markdown_text)

@pytest.fixture
def markdowns(markdown, file_markdown):
    return markdown, file_markdown

def test_markdowns(markdowns):
    strings = dict(HTML_text='café animate noun',
                   Typing='caf(e *kinship*',
                   Display='café *kinship*')
    for markdown in markdowns:
        for string in strings.values():
            assert markdown.to_markdown(string) == strings['Display']
            assert markdown.to_markup(string) == strings['HTML_text']

def test_iadd(markdown):
    markdown += dict(markup='alpha', markdown='beta', display_markdown=False)
    assert len(markdown.replacements) == 3
    assert markdown[-1] == dict(markup='alpha', markdown='beta', display_markdown=False)