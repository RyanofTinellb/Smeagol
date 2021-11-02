class SiteError(BaseException):
    '''Base class for All errors raised by
        smeagol.site.site.Site'''


class FileNotFound(FileNotFoundError):
    '''Base class for File errors'''


class SiteFileError(SiteError, FileNotFound):
    '''Base class for File errors raised by
        smeagol.site.site.Site'''


class SourceFileNotFound(SiteFileError):
    '''Raised when Site cannot find .src file'''


class TemplateFileNotFound(SiteFileError):
    '''Raised when Site cannot find .html file'''


class SectionFileNotFound(SiteFileError):
    '''Raised when Site cannot find .html file'''


class WholepageTemplateFileNotFound(SiteFileError):
    '''Raised when Site cannot find .html file'''


class SearchTemplateFileNotFound(SiteFileError):
    '''Raised when Site cannot find .html file'''


class Search404TemplateFileNotFound(SiteFileError):
    '''Raised when Site cannot find .html file'''


class MarkdownError(BaseException):
    '''Base class for all errors raised by
        smeagol.translation.markdown.Markdown'''


class MarkdownFileNotFound(MarkdownError, FileNotFound):
    '''Raised when Markdown cannot find .mkd file'''

def throw_error(err, obj, attr):
    name = obj.__class__.__name__
    return err(f"'{name}' object has no attribute '{attr}'")