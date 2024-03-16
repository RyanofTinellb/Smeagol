import re
import os
import random
from smeagol.utilities.filesystem import start_server, open_in_browser

ROOT = 'c:/users/ryan/tinellbianlanguages'
folders = list(os.walk(ROOT))[0][1]
folders = list(filter(lambda x: re.match(r'\w', x), folders))
PROMPT = '\n'.join(
    [f'{i}. {k}' for i, k in enumerate(folders, start=1)]) + '\n\n? '
folder = folders[int(input(PROMPT)) - 1]
PORT = start_server(random.randint(30000, 65535), os.path.join(ROOT, folder))
open_in_browser(PORT)
print()
