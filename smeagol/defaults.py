class default:
    markdown = '''<!DOCTYPE text/html>
( | &lparen; | <br>
) | &rparen; | <br>
_ | &under; | <br>
' | &squot; | <br>
&aacute; | (a | <br>
&eth; | (d | <br>
&thorn; | (t | <br>
&eacute; | (e | <br>
&iacute; | (i | <br>
&oacute; | (o | <br>
&uacute; | (u | <br>
&agrave; | )a | <br>
&egrave; | )e | <br>
&igrave; | )i | <br>
&ograve; | )o | <br>
&#x1e6c; | )T | <br>
&#x1e6d; | )t | <br>
&ugrave; | )u | <br>
&acirc; | ()a | <br>
&ecirc; | ()e | <br>
&icirc; | ()i | <br>
&ocirc; | ()o | <br>
&ucirc; | ()u | <br>
&#x17e; | )(z | <br>
&ntilde; | !!n | <br>
&atilde; | !!a | <br>
&otilde; | !!o | <br>
h&#x330; | !!h | <br> <!-- h with tilde below -->
l&#x330; | !!l | <br> <!-- l with tilde below -->
&auml; | !a | <br>
&euml; | !e | <br>
&iuml; | !i | <br>
&ouml; | !o | <br>
&uuml; | !u | <br>
&#x323; | :d | <!--underdot--> <br>
&#x101; | _a | <!--a macron--> <br>
&#x113; | _e | <!--e macron--> <br>
&#x12b; | _i | <!--i macron--> <br>
&#x14d; | _o | <!--o macron--> <br>
&#x16b; | _u | <!--u macron--> <br>
&#x157; | ,r | <!--r cedilla--> <br>
&rsquo; | ' | <br>
&#x294; | '' | <!--glottal stop--> <br>
&middot; | .. | <br>
&lparen; | \( | <br>
&rparen; | )/ | <br>
&under; | \\_ | <br>
&squot; | \\' | <br>
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
          "text": "404 Page Not Found File Template",
          "action": "open",
          "extension": ".html"
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
