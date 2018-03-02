class default:
    markdown = '''<!DOCTYPE text/html>
( | &lparen; | <br>
) | &rparen; | <br>
_ | &under; | <br>
' | &squot; | <br>
&aacute; | (a | <br>
&eacute; | (e | <br>
&iacute; | (i | <br>
&oacute; | (o | <br>
&uacute; | (u | <br>
&agrave; | )a | <br>
&egrave; | )e | <br>
&igrave; | )i | <br>
&ograve; | )o | <br>
&ugrave; | )u | <br>
&acirc; | $a | <br>
&ecirc; | $e | <br>
&icirc; | $i | <br>
&ocirc; | $o | <br>
&ucirc; | $u | <br>
&auml; | :a | <br>
&euml; | :e | <br>
&iuml; | :i | <br>
&ouml; | :o | <br>
&uuml; | :u | <br>
&#x323; | :d | <!--underdot--> <br>
&#x101; | _a | <!--a macron--> <br>
&#x113; | _e | <!--e macron--> <br>
&#x12b; | _i | <!--i macron--> <br>
&#x14d; | _o | <!--o macron--> <br>
&#x16b; | _u | <!--u macron--> <br>
&#x157; | ,r | <!--r cedilla--> <br>
&rsquo; | ' | <br>
&#x294; | '' | <!--glottal stop--> <br>
&middot; | . | <br>
&lparen; | \( | <br>
&rparen; | )/ | <br>
&under; | \\_ | <br>
&squot; | \\' | <br>
'''

    config = '''
    {
      "site": {
        "name": "",
        "destination": ""
      },
      "files": {
        "searchjson": "",
        "source": "",
        "template": ""
      },
      "random words": {
        "number": 0,
        "geminate": 1
      },
      "current page": [
      ]
      "markdown": "",
      "links": [
      ]
    }
    '''

    properties = '''
    [
      {
        "name": "Destination",
        "property": "destination",
        "owner": "site",
        "check": false,
        "textbox": true,
        "browse": "folder",
        "vartype": "string"
      },
      {
        "name": "Name",
        "property": "name",
        "owner": "site",
        "check": false,
        "textbox": true,
        "browse": false,
        "vartype": "string"
      },
      {
        "name": "Data File",
        "property": "source",
        "owner": "files",
        "check": false,
        "textbox": true,
        "vartype": "string",
        "browse": {
          "action": "save",
          "text": "Data File",
          "extension": ".txt"
        }
      },
      {
        "name": "Template",
        "property": "template",
        "owner": "files",
        "check": false,
        "textbox": true,
        "vartype": "string",
        "browse": {
          "text": "HTML Template",
          "action": "open",
          "extension": ".html"
        }
      },
      {
        "name": "Searchterms File",
        "property": "searchjson",
        "owner": "files",
        "check": false,
        "textbox": true,
        "vartype": "string",
        "browse": {
          "text": "JSON File",
          "action": "save",
          "extension": ".json"
        }
      },
      {
        "name": "Number of Random Words",
        "property": "number",
        "owner": "random words",
        "vartype": "integer",
        "check": false,
        "textbox": true,
        "browse": false
      },
      {
        "name": "Odds of Gemination",
        "owner": "random words",
        "property": "geminate",
        "vartype": "integer",
        "check": false,
        "textbox": true,
        "browse": false
      },
      {
        "name": "Version Links within Stories",
        "property": "InternalStory",
        "owner": "links",
        "check": true,
        "textbox": false,
        "browse": false
      },
      {
        "name": "Links within Dictionaries",
        "property": "InternalDictionary",
        "owner": "links",
        "check": true,
        "textbox": false,
        "browse": false
      },
      {
        "name": "Links to an external Grammar",
        "property": "ExternalGrammar",
        "owner": "links",
        "check": true,
        "textbox": true,
        "vartype": "string",
        "browse": {
          "text": "Grammar Links File",
          "action": "open",
          "extension": "*.glk"
        }
      },
      {
        "name": "Glossing Abbreviation Tooltips",
        "property": "Glossary",
        "owner": "links",
        "check": true,
        "textbox": true,
        "vartype": "string",
        "browse": {
          "text": "Glossary File",
          "action": "open",
          "extension": "*.gls"
        }
      },
      {
        "name": "Links to an external Dictionary",
        "property": "ExternalDictionary",
        "owner": "links",
        "check": true,
        "textbox": true,
        "vartype": "string",
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
                  {content}
                  {nav-footer}
                  {copyright}'''
