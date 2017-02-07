import cProfile
import random


def blah():
    for _ in range(900):
        with open("hey.txt", "w") as f:
            f.write(str(random.randint(0, 1000)))

cProfile.run('blah()')
