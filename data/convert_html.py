
import re
from html import unescape
import sys
 
def html_to_plain_text(html):
    text = re.sub('<head.*?>.*?</head>', '', html, flags=re.M | re.S | re.I)
    #text = re.sub('<a\s.*?>', ' HYPERLINK ', text, flags=re.M | re.S | re.I)
    text = re.sub('<.*?>', ' ', text, flags=re.M | re.S)
    #text = re.sub(r'(\s*\n)+', '\n', text, flags=re.M | re.S)
    return unescape(text)

if __name__ == "__main__":
    for line in open(sys.argv[1], 'r').readlines():
        print(html_to_plain_text(line.strip()))
        continue
        fields = line.split(",")
        if len(fields) != 2:
            continue
        print(html_to_plain_text(fields[0].strip()))
