from sites import Grammar
from smeagol.editor.addremovelinks import AddRemoveLinks
from smeagol.translation.markdown import Markdown

d = Grammar()
i = AddRemoveLinks(dict(
    Glossary="C:/Users/Ryan/Documents/TinellbianLanguages/grammar/glossary.gls",
    ExternalDictionary="http://dictionary.tinellb.com"
))
m = Markdown('c:/users/ryan/documents/tinellbianlanguages/grammar/grammar.mkd')
for entry in d:
    old = str(entry)
    text = i.remove_links(old)
    text = m.to_markdown(text)
    text = m.to_markup(text)
    text = i.add_links(text, entry)
    if old <> text:
        entry.text = text
        entry.publish(d.template)
        print entry.name
d.update_source()
