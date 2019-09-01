class default:
    markdown = '''<!DOCTYPE text/html>
á | (a | s<br>
é | (e | s<br>
í | (i | s<br>
ó | (o | s<br>
ú | (u | s<br>
à | )a | s<br>
è | )e | s<br>
ì | )i | s<br>
ò | )o | s<br>
Ṭ | )T | s<br>
ṭ | )t | s<br>
ù | )u | s<br>
â | ()a | s<br>
ê | ()e | s<br>
î | ()i | s<br>
ô | ()o | s<br>
û | ()u | s<br>
ž | )(z | s<br>
ñ | !!n | s<br>
ã | !!a | s<br>
õ | !!o | s<br>
h̰ | !!h | s<br>
l̰ | !!l | s<br>
ä | !a | s<br>
ë | !e | s<br>
ï | !i | s<br>
ö | !o | s<br>
ü | !u | s<br>
ā | _a | s<br>
ē | _e | s<br>
ī | _i | s<br>
ō | _o | s<br>
ū | _u | s<br>
ŗ | ,r | s<br>
’ | ' | s<br>
ʔ | '' | s<br>
· | .. | s<br>
'''

    config = '''
{
  "site": {
    "name": "",
    "destination": "",
    "files": {
      "source": "",
      "template_file": "",
      "wordlist": "",
      "wholepage": {
        "file": "",
        "template": ""
      },
      "search": {
        "index": "",
        "template": "",
        "page": "",
        "template404": "",
        "page404": ""
      }
    }
  },
  "sample texts": "",
  "current": {
    "page": [
      ""
    ],
    "markdown": "",
    "language": "en: English",
    "position": "1.0",
    "fontsize": 14
  },
  "links": {}
}
    '''

    page404 = '''<!DOCTYPE html>
    <html>

    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" type="text/css" href="/basic_style.css">
      <link rel="stylesheet" type="text/css" href="/style.css">
      <link rel="icon" type="image/png" href="/favicon.png">
      <title>404 - Page Not Found</title>
    </head>

    <body>
      <div class="flex">
        <div class="nav-pane">
        {0}
        </div>
        <div class="content">
          <h1>404 - Page Not Found</h1>
          <p class="introduction">Use this search page to get back on track, or choose an option from the navigation pane.</p>
          <p class="introduction"></p>
          <form>
            <input type="text" class="term" id="term" name="term" placeholder="Search-" autofocus><br>
            <input type="submit" class="submit" value="Search">
            <input type="radio" name="andor" id="and" value="and" checked="true">AND
            <input type="radio" name="andor" id="or" value="or">OR
          </form>
          <div class="results" id="results" name="results"></div>
          <script src="/search.js"></script>
          <script src="/404search.js"></script>
        </div>
      </div>
    </body>

    </html>'''

    properties = '''
    [
      {
        "name": "Name",
        "property": "name",
        "owner": "site",
        "textbox": true,
        "browse": false
      },
      {
        "name": "Destination",
        "property": "destination",
        "owner": "site",
        "textbox": true,
        "browse": "folder"
      },
      {
        "name": "Data File",
        "property": "source",
        "owner": "files",
        "textbox": true,
        "browse": {
          "action": "save",
          "text": "Data File",
          "extension": ".src"
        }
      },
      {
        "name": "Template",
        "property": "template_file",
        "owner": "files",
        "textbox": true,
        "browse": {
          "text": "HTML Template",
          "action": "open",
          "extension": ".html"
        }
      },
      {
        "name": "Wordlist",
        "property": "wordlist",
        "owner": "files",
        "textbox": true,
        "browse": {
          "text": "Wordlist File",
          "action": "open",
          "extension": ".json"
        }
      },
      {
        "name": "Sample Texts",
        "property": "sample_texts",
        "owner": "random words",
        "textbox": true,
        "browse": {
          "text": "Source File",
          "action": "open multiple",
          "extension": ".src"
        }
      },
      {
        "name": "Wholepage:"
      },
      {
        "name": "--Location",
        "property": "wholepage_file",
        "owner": "files/wholepage",
        "textbox": true,
        "browse": {
          "text": "Wholepage File",
          "action": "save",
          "extension": ".html"
        }
      },
      {
        "name": "--Template",
        "property": "wholepage_template",
        "owner": "files/wholepage",
        "textbox": true,
        "browse": {
          "text": "Wholepage Template",
          "action": "open",
          "extension": ".html"
        }
      },
      {
        "name": "Search:"
      },
      {
        "name": "--Location",
        "property": "search_page",
        "owner": "files/search",
        "textbox": true,
        "browse": {
          "text": "Seach Page Location",
          "action": "save",
          "extension": ".html"
        }
      },
      {
        "name": "--Template",
        "property": "search_template",
        "owner": "files/search",
        "textbox": true,
        "browse": {
          "text": "Search Page Template",
          "action": "open",
          "extension": ".html"
        }
      },
      {
        "name": "--404 Location",
        "property": "search_page404",
        "owner": "files/search",
        "textbox": true,
        "browse": {
          "text": "404 Page Not Found File",
          "action": "save",
          "extension": ".html"
        }
      },
      {
        "name": "--404 Template",
        "property": "search_template404",
        "owner": "files/search",
        "textbox": true,
        "browse": {
          "text": "404 Page Not Found File Template",
          "action": "open",
          "extension": ".html"
        }
      },
      {
        "name": "--Index",
        "property": "search_index",
        "owner": "files/search",
        "textbox": true,
        "browse": {
          "text": "Search Index",
          "action": "open",
          "extension": ".json"
        }
      },
      {
        "name": "Links:"
      },
      {
        "name": "--Internal Dictionaries",
        "property": "InternalDictionary",
        "owner": "links",
        "textbox": false,
        "browse": false
      },
      {
        "name": "--External Grammar",
        "property": "ExternalGrammar",
        "owner": "links",
        "textbox": true,
        "browse": {
          "text": "Grammar Links File",
          "action": "open",
          "extension": ".glk"
        }
      },
      {
        "name": "--Glossing Abbreviation Tooltips",
        "property": "Glossary",
        "owner": "links",
        "textbox": true,
        "browse": {
          "text": "Glossary File",
          "action": "open",
          "extension": ".gls"
        }
      },
      {
        "name": "--External Dictionary",
        "property": "ExternalDictionary",
        "owner": "links",
        "textbox": true,
        "browse": false
      }
    ]
    '''

    template = '''<!DOCTYPE html>
            <html>
              <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta charset="utf-8">
                <title>
                  {category-title}
                </title>
              </head>
              <body>
                {family-links}
                  {nav-footer}
                  {main-contents}
                  {nav-footer}
                  {copyright}'''
