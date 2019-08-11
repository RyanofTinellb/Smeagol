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
      "searchindex": "",
      "source": "",
      "template_file": ""
    }
  },
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
            <input type="text" class="term" id="term" name="term" placeholder="Search..." autofocus><br>
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
          "extension": ".json"
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
        "name": "Searchterms File",
        "property": "searchindex",
        "owner": "files",
        "textbox": true,
        "browse": {
          "text": "JSON File",
          "action": "save",
          "extension": ".json"
        }
      },
      {
        "name": "Wordlist",
        "property": "wordlist",
        "owner": "files",
        "textbox": true,
        "browse": {
          "text": "Wordlist File",
          "action": "save",
          "extension": ".json"
        }
      },
      {
        "name": "Links within Dictionaries",
        "property": "InternalDictionary",
        "owner": "links",
        "textbox": false,
        "browse": false
      },
      {
        "name": "Links to an external Grammar",
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
        "name": "Glossing Abbreviation Tooltips",
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
        "name": "Links to an external Dictionary",
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
