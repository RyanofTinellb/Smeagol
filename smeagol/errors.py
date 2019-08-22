class SiteError(BaseException):
    '''Base class for All errors raised by
        smeagol.site.site.Site'''

class SiteFileError(SiteError, FileNotFoundError):
    '''Base class for File errors raised by
        smeagol.site.site.Site'''

class SourceFileNotFoundError(SiteFileError):
    '''Raised when Site cannot find .src file'''

class TemplateFileNotFoundError(SiteFileError):
    '''Raised when Site cannot find .html file'''

class WholepageTemplateFileNotFoundError(SiteFileError):
    '''Raised when Site cannot find .html file'''

class SearchTemplateFileNotFoundError(SiteFileError):
    '''Raised when Site cannot find .html file'''

class Search404TemplateFileNotFoundError(SiteFileError):
    '''Raised when Site cannot find .html file'''

class MarkdownError(BaseException):
    '''Base class for all errors raised by
        smeagol.translation.markdown.Markdown'''

class MarkdownFileNotFoundError(MarkdownError, FileNotFoundError):
    '''Raised when Markdown cannot find .mkd file'''