import sys
import random

if __name__ == "__main__":
    fileName = sys.argv[1]
    f = open(fileName, "r")
    lines = f.readlines()
    random.shuffle(lines)
    length = len(lines)
    i = 0
    j = length - 1
    while i < j:
        print(lines[i].strip())
        print(lines[j].strip())
        i = i + 1
        j = j - 1
