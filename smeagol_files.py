from translation import Markdown

class Files:
    def __init__(self, source='', template='', markdown='', searchjson=''):
        """
        All parameters are strings of the form 'c:/path/filename.ext'
        """
        self.source = source
        self.template_file = template
        with open(self.template_file) as template:
            self.template = template.read()
        self.markdown_file = markdown
        self.markdown = Markdown(self.markdown_file)
        self.searchjson = searchjson
