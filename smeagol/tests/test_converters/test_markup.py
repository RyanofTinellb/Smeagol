from smeagol.conversion import Markup
import pytest

@pytest.fixture
def markup():
    return Markup()

def test_tables(markup):
    orig = '''<table>
r2c2 |hr2 1st person |hr2 2nd person |hc3 3rd person
h topic |h animate |h inanimate
hc2 intranstitive | ’usu | filli | (su’a) | mihu | pa
hc2 transitive | suma | fu | (su’a) | quhu | ’iffa
hc2 ablative | puttu | sacu | raja | kassi | kalu
hc2 dative | pixi | ba’u | datu | jusi | ku
hr2 genitive |h (alienable) | pagu | ba | su’a | disi |
h (inalienable) | -pahi | -ba ||| -qa
</table>'''
    table = '''<table>
<tr><td rowspan="2" colspan="2"></td> <th rowspan="2">1st person</th> <th rowspan="2">2nd person</th> <th colspan="3">3rd person</th></tr>
<tr><th>topic</th> <th>animate</th> <th>inanimate</th></tr>
<tr><th colspan="2">intranstitive</th> <td>’usu</td> <td>filli</td> <td>(su’a)</td> <td>mihu</td> <td>pa</td></tr>
<tr><th colspan="2">transitive</th> <td>suma</td> <td>fu</td> <td>(su’a)</td> <td>quhu</td> <td>’iffa</td></tr>
<tr><th colspan="2">ablative</th> <td>puttu</td> <td>sacu</td> <td>raja</td> <td>kassi</td> <td>kalu</td></tr>
<tr><th colspan="2">dative</th> <td>pixi</td> <td>ba’u</td> <td>datu</td> <td>jusi</td> <td>ku</td></tr>
<tr><th rowspan="2">genitive</th> <th>(alienable)</th> <td>pagu</td> <td>ba</td> <td>su’a</td> <td>disi</td> <td></td></tr>
<tr><th>(inalienable)</th> <td>-pahi</td> <td>-ba</td> <td></td> <td></td> <td>-qa</td></tr>
</table>'''
    assert markup.html(orig) == table