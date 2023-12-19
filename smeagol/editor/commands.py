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


def textbox(obj):
    return [
        ('<Control-r>', obj.refresh_random),
        ('<Control-s>', obj.save_page),
        ('<Control-t>', obj.new_tab),
        ('<Control-T>', obj.reopen_tab),
        ('<Control-w>', obj.close_tab),
        ('<Enter>', obj.reset_entry),
    ]


def heading(obj):
    return [
        ('<Prior>', obj.previous_entry),
        ('<Next>', obj.next_entry),
        ('<Return>', obj.load_entry),
    ]


def language(obj):
    return [('<<ComboboxSelected>>', obj.change_language)]


def random(obj):
    return [
        ('<Button-1>', obj.refresh_random),
        ('<Button-3>', obj.clear_random),
    ]
