def menu(obj):
    return [
        ('Site', [
            ('Open', obj.open_site),
            ('Save', obj.save_site),
            ('Save _As', obj.save_site_as),
        ]),
        ('Page', [
            ('Rename', obj.rename_page),
            ('Open in Browser', obj.open_entry_in_browser),
        ]),
        ('Edit', [
            ('Styles', obj.edit_styles),
            ('Markdown', obj.markdown_edit),
            ('Templates', obj.template_edit),
        ]),
    ]


def language(obj):
    return [('<<ComboboxSelected>>', obj.change_language)]


def random(obj):
    return [
        ('<Button-1>', obj.refresh_random),
        ('<Button-3>', obj.clear_random),
    ]
