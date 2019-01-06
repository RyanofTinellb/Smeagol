from sites import Dictionary
from smeagol.editor.addremovelinks import AddRemoveLinks
from smeagol.translation.markdown import Markdown

d = Dictionary()
i = AddRemoveLinks(dict(ExternalGrammar="c:/users/ryan/documents/tinellbianlanguages/dictionary/links.glk"))
m = Markdown('c:/users/ryan/documents/tinellbianlanguages/dictionary/dictionary.mkd')
for entry in d:
    old = str(entry)
    text = i.remove_links(old)
    text = m.to_markdown(text)
    text = text.replace('List of Elements', '*elements*')
    text = m.to_markup(text)
    text = i.add_links(text, entry)
    if old <> text:
        entry.text = text
        entry.publish(d.template)
        print entry.name
d.update_source()
