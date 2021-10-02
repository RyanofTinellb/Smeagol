import json

class default:
    markdown = [
  {
    "markup": "á",
    "markdown": "(a",
    "display_markdown": False
  },
  {
    "markup": "é",
    "markdown": "(e",
    "display_markdown": False
  },
  {
    "markup": "í",
    "markdown": "(i",
    "display_markdown": False
  },
  {
    "markup": "ó",
    "markdown": "(o",
    "display_markdown": False
  },
  {
    "markup": "ú",
    "markdown": "(u",
    "display_markdown": False
  },
  {
    "markup": "à",
    "markdown": ")a",
    "display_markdown": False
  },
  {
    "markup": "è",
    "markdown": ")e",
    "display_markdown": False
  },
  {
    "markup": "ì",
    "markdown": ")i",
    "display_markdown": False
  },
  {
    "markup": "ò",
    "markdown": ")o",
    "display_markdown": False
  },
  {
    "markup": "Ṭ",
    "markdown": ")T",
    "display_markdown": False
  },
  {
    "markup": "ṭ",
    "markdown": ")t",
    "display_markdown": False
  },
  {
    "markup": "ù",
    "markdown": ")u",
    "display_markdown": False
  },
  {
    "markup": "â",
    "markdown": "()a",
    "display_markdown": False
  },
  {
    "markup": "ê",
    "markdown": "()e",
    "display_markdown": False
  },
  {
    "markup": "î",
    "markdown": "()i",
    "display_markdown": False
  },
  {
    "markup": "ô",
    "markdown": "()o",
    "display_markdown": False
  },
  {
    "markup": "û",
    "markdown": "()u",
    "display_markdown": False
  },
  {
    "markup": "ž",
    "markdown": ")(z",
    "display_markdown": False
  },
  {
    "markup": "ñ",
    "markdown": "!!n",
    "display_markdown": False
  },
  {
    "markup": "ã",
    "markdown": "!!a",
    "display_markdown": False
  },
  {
    "markup": "õ",
    "markdown": "!!o",
    "display_markdown": False
  },
  {
    "markup": "h̰",
    "markdown": "!!h",
    "display_markdown": False
  },
  {
    "markup": "l̰",
    "markdown": "!!l",
    "display_markdown": False
  },
  {
    "markup": "ä",
    "markdown": "!a",
    "display_markdown": False
  },
  {
    "markup": "ë",
    "markdown": "!e",
    "display_markdown": False
  },
  {
    "markup": "ï",
    "markdown": "!i",
    "display_markdown": False
  },
  {
    "markup": "ö",
    "markdown": "!o",
    "display_markdown": False
  },
  {
    "markup": "ü",
    "markdown": "!u",
    "display_markdown": False
  },
  {
    "markup": "ā",
    "markdown": "_a",
    "display_markdown": False
  },
  {
    "markup": "ē",
    "markdown": "_e",
    "display_markdown": False
  },
  {
    "markup": "ī",
    "markdown": "_i",
    "display_markdown": False
  },
  {
    "markup": "ō",
    "markdown": "_o",
    "display_markdown": False
  },
  {
    "markup": "ū",
    "markdown": "_u",
    "display_markdown": False
  },
  {
    "markup": "ŗ",
    "markdown": ",r",
    "display_markdown": False
  },
  {
    "markup": "ʔ",
    "markdown": "''",
    "display_markdown": False
  },
  {
    "markup": "’",
    "markdown": "'",
    "display_markdown": False
  },
  {
    "markup": "·",
    "markdown": "..",
    "display_markdown": False
  }
]

    config = json.loads('''
      {}
    ''')

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
        "property": "template",
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
