from smeagol.conversion.text_tree.node import Node
from smeagol.editor.interface.interface import Interface

i = Interface('c:/users/ryan/tinellbianlanguages/grammar/data/config.smg', server=False)
k = i.site['A Grammar of the Tinellbian Languages', 'Languages', 'Lulani', 'High', 'Sample Text'].text
        
sample = [n for n in k.nodes if n.name == 'sample'][0]
interlinear = [n for n in k.nodes if n.name == 'interlinear'][0]
sample.children = [para(paragraph) for paragraph in interlinear.nodes]

def para(paragraph):
    return ('<tinellbian@x-tlb-hl>' + '</tinellbian@x-tlb-hl>\n<tinellbian@x-tlb-hl>'.join([line.middle_text for line in paragraph.nodes if line.name.startswith('tinellbian')]) 
