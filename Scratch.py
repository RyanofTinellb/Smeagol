import re

k = 'a'

k = re.sub('aa+', 'a', k)

print(k)
