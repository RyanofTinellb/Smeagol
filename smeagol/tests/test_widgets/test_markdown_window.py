import pytest
import tkinter as Tk
from ...conversion import Markdown
from ...widgets.markdown_window import MarkdownWindow

@pytest.fixture
def markdown():
    return Markdown([
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
    ])

@pytest.fixture
def top():
    return Tk.Tk()

@pytest.fixture
def blank_window(top):
    return MarkdownWindow(top)

@pytest.fixture
def window_with_markdown(top, markdown):
    return MarkdownWindow(top, markdown)

# def test_window(blank_window):
#     blank_window.mainloop()

# def test_markdown_window(window_with_markdown):
#     window_with_markdown.mainloop()