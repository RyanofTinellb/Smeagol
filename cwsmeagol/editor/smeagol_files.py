from cwsmeagol.defaults import default

class Files:
    def __init__(self, source='', template='', searchjson=''):
        """
        All parameters are strings of the form 'c:/path/filename.ext'
        """
        self.source = source
        self.template_file = template
        try:
            with open(self.template_file) as template:
                self.template = template.read()
        except IOError:
            self.template = None
        self.searchjson = searchjson
