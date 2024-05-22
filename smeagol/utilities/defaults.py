import json
from dataclasses import dataclass

# pylint: disable=C0103


@dataclass
class default:
    font = {'font': 'Calibri',
             'size': 12}

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
