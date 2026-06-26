import json
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
FILENAME = 'c:/users/ryan/tinellbianlanguages/www/data/assets/eplist.json'


def update(ep):
    with utils.ignored(KeyError, TypeError):
        pass


fs.update(FILENAME, update, is_json=True)


def is_nonempty(ep):
    return ep and ep['date'] != '00000000'


def jsonify(ep):
    return json.dumps(ep, ensure_ascii=False)


def change(eplist):
    eps = ',\n'.join([jsonify(ep) for ep in sorted(
        eplist, key=epsorter) if is_nonempty(ep)])
    return f'[{eps}]'


def epsorter(ep):
    series = ep.get('series')
    if isinstance(series, int):
        series_number, series_id = series, ''
    elif isinstance(series, str):
        series_number, series_id = 0, series
    elif isinstance(series, type(None)):
        series_number, series_id = 0, ''
    else:
        series_number, series_id = series['number'], series['name']

    meta = (ep.get('meta', series_id) or
            (isinstance(p := ep.get('ep', 'zzzz'), dict) and p['name']) or
            p)

    season = ep.get('season', 0)
    if isinstance(season, dict):
        season = season.get('number')
    elif isinstance(season, str):
        season = 0

    multi = ep.get('multi')
    ordinal = multi.get('ordinal', 0) if isinstance(multi, dict) else 0

    date = ep.get('date', '00000000')
    episode = ep.get('ep')
    number = episode.get('number', 0) if isinstance(
        episode, dict) else 0
    wallet = ep.get('location', {}).get('wallet')
    space = ep.get('location', {}).get('space')
    return meta, series_number, season, number, ordinal, date, wallet, space


fs.change(FILENAME, change, is_json=True)
