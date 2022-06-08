import os
import sys
import random

def print_usage():
    print("usage: {} <number of vertices, maximum budget, number of burnt vertices, filename>".format(sys.argv[0]))
    sys.exit(1)

if len(sys.argv) != 5:
    print_usage()
n = int(sys.argv[1])
b = int(sys.argv[2])
s = int(sys.argv[3])

fp = open(sys.argv[4], "w")

fp.write("{} {}\n".format(n, b))
for i in range(1, n):
    j = random.randint(0, i - 1)
    fp.write("{} {}\n".format(i, j))
fp.write("{}\n".format(s))
ids = []
for i in range(s):
    ids.append(1)
for i in range(s, n):
    ids.append(0)
random.shuffle(ids)
for i in range(n):
    if ids[i]:
        fp.write("{} ".format(i))
fp.close()