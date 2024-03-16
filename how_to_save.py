# pylint: skip-file
'''
    * Create T from textbox dump
    * T -> S
    * Save S to .src
    * T -> H
    * Save H to .html
'''

def save_entry(self):
    t = TextTree(textbox.formatted_text)
    update_entry(entry, texttree)
    
    entry.save
    interface.save(entry)

@Tab
def update_entry(self):
    self.entry.text = self.textbox.formatted_text
    self.interface.save_site()

