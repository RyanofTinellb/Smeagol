import pytest
from ...widgets import Textbox


@pytest.fixture
def textbox():
    return Textbox()


def test_tagger(textbox):
    orig_text = '<tag>Text</tag>'
    textbox.insert(orig_text)
    textbox.hide_tags()
    textbox.show_tags()
    assert textbox.text == orig_text