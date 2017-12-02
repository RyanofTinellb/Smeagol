from cwsmeagol.translation import Markdown

class Files:
    def __init__(self, source='', template='', searchjson=''):
        """
        All parameters are strings of the form 'c:/path/filename.ext'
        """
        self.source = source
        self.template_file = template
        if template:
            with open(self.template_file) as template:
                self.template = template.read()
        else:
            self.template = None
        self.searchjson = searchjson
