with open('../thecoelacanthquartet/data.txt') as f:
    page = f.read()
page = page.split('[1]')[1:]
page = map(lambda x: x.split('[3]')[1], page)
page = map(lambda x: x.splitlines(), page)
page = zip(*page)
output = ''
for entry in page:
    for line in entry:
        output += line + '\n'
    output += '\n'
with open('c:/users/ryan/desktop/practice.txt', 'w') as g:
    g.write(output)
