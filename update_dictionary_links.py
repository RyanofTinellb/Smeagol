from sites import Dictionary
from smeagol.editor.addremovelinks import AddRemoveLinks

d = Dictionary()
i = AddRemoveLinks(dict(ExternalGrammar="c:/users/ryan/documents/tinellbianlanguages/dictionary/links.glk"))
for entry in d:
    old = str(entry)
    text = i.remove_links(old)
    text = i.add_links(text, entry)
    if old != text:
        entry.text = text
        entry.publish(d.template)
        print(entry.name)
d.update_source()
