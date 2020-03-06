import pytest
from smeagol import Editor, Site


@pytest.fixture
def editor():
    return Editor()


@pytest.fixture
def site():
    s = Site()
    s.tree = dict(name='a', children=[
        dict(name='b', children=[
            dict(name='d'),
            dict(name='e'),
            dict(name='f')
        ]),
        dict(name='c'),
    ])
    return s


class Object:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_previous_entry(editor, site):
    editor.textbox.interface.site = site
    h = editor.headings
    h.add_heading()
    h.add_heading()
    h.add_heading()
    h.headings = ['b', 'e']
    editor.previous_entry(Object(widget=h._headings[1]))

    assert editor.headings.headings == ['b', 'd']
