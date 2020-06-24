
#encoding=utf-8
import sys
import re
import random
import numpy as np
import unicodedata

def random_choice(weight_vector):
    #根据权重随机挑选一个
    total = np.sum(weight_vector)
    normalized = [w / total for w in weight_vector]
    for index in range(1, len(normalized)):
        normalized[index] += normalized[index-1]
    choice = random.random()
    for index in range(0, len(normalized)):
        if normalized[index] > choice:
            return index
    #return len(weight_vector)

def pinyin_distance(a, b):
    #计算两个拼音的距离，越小越相似
    pa = a.strip("012345")
    pb = b.strip("012345")
    dis = 0
    if a[-1] != b[-1]:
        dis += 3
    if a[0] != b[0]:
        return 1000
    if pa[-1] != pb[-1] and pa[-1] != 'g' and pb[-1] != 'g':
        return 1000
    if a == b:
        return 0
    if pa == pb:
        return 1 + dis
    if pa[0] in ('s','z', 'c'):
        pa = pa[1:].strip('h')
        pb = pb[1:].strip('h')
        if pa == pb:
            return 1+dis
    if pa[-1] == 'g':
        pa = pa[:-1]
    if pb[-1] == 'g':
        pb = pb[:-1]
    if pa == pb:
        return 10+dis
    return 1000

control_chars = ''.join([c for c in map(chr, list(range(0,32)) + list(range(127,160)))])
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):

    return control_char_re.sub('', s)

def dict2list(d):
    res = []
    for k,v in d.items():
        res.append((k, v))
    return res

def is_chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def have_chinese(sentence):
    for ch in sentence:
        if is_chinese(ch):
            return True
    return False

def is_number(ch):
    if ch >= '0' and ch <= '9':
        return True
    return False

def is_alphabet(ch):
    if (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z'):
        return True
    return False

def chapter_to_sentences(chapter):
    sentences = []
    sentence = ""
    stop_ch = ["。", " ", "，", "？", "！","；","…", "?", "!"]
    last_ch = ""
    next_ch = ""
    left_brackets = ["{", "[", "【", "「", "(", "（", "“", "‘", "<"]
    right_brackets = ["}", "]", "】", "」", ")", "）", "”", "’", ">"]
    matcher = {"}":"{", "]":"[", "】":"【","」":"「",")":"(", "）":"（", "”":"“", "’":"‘", ">":"<"}
    brackets_vis = {}
    brackets_close = True
    inline_content_max_length = 15
    inline_count = 0
    for index in range(len(chapter)):
        ch = chapter[index]
        if index < len(chapter) - 1:
            next_ch = chapter[index+1]
        sentence += ch
        inline_count += 1
        if ch in stop_ch or (ch == ',' and (is_chinese(last_ch) or is_chinese(next_ch))) \
                or (ch=="." and is_number(last_ch)==False):
            if brackets_close == True or inline_count > inline_content_max_length:
                sentences.append(sentence)
                sentence = ""
                brackets_vis.clear()
                brackets_close = True
        if ch in left_brackets:
            brackets_vis[ch] = True
            brackets_close = False
            inline_count = 0
        elif ch in right_brackets:
            if matcher[ch] in brackets_vis:
                del brackets_vis[matcher[ch]]
                if len(brackets_vis) == 0:
                    brackets_close = True

        last_ch = ch
    if len(sentence) > 0:
        sentences.append(sentence)
    return sentences

def strip_punctuation(sentence):
    return sentence.strip("。，‘’“”？！；～…?!,.　")

def gather_sentences(sentences, max_length=50):
    long_sentences = []
    long_sentence = ""
    placeholder_num = 5
    for index in range(len(sentences)):
        sentence = sentences[index]
        if len(sentence) == 0:
            continue
        if len(sentence) < 10:
            if sentence[-1] in (",", "，") and index < len(sentences)-1:
                s = sentences[index] + sentences[index+1]
                if len(s) < max_length-placeholder_num:
                    sentences[index+1] = s
                    sentences[index] = ""
                    continue
            if index > 0:
                s = sentences[index-1] + sentences[index]
                if len(s) < max_length-placeholder_num:
                    sentences[index-1] = s 
                    sentences[index] = ""

                
                
    for sentence in sentences:
        if len(long_sentence) > max_length/2 or len(long_sentence)+len(sentence) > max_length - 10:
            s = long_sentence.strip("# ")
            if len(s) > 0:
                long_sentences.append(s)
            long_sentence = ""
        long_sentence += sentence
    if len(long_sentence.strip("# ")) > 0:
        long_sentences.append(long_sentence.strip("# "))
    return long_sentences

def format_white_space(content):
    result = ""
    last = 1
    content = list(content)
    for index in range(len(content)):
        ch = content[index]
        if ch in ("\n", "\t", "\r") or unicodedata.category(ch) in ("Zs", "Zp", "Zl"):
            if last == 0 and index > 0 and is_punctuation(content[index-1])==False:
                ch = "# "
            else:
                ch = ""
            last = 1
        else:
            last = 0
            
        result += ch
    return result

def remove_control_character(content):
    result = ""
    for ch in content:
        if ch not in ("\t", "\n", "\r") and unicodedata.category(ch) in ("Cc", "Cf"):
            continue
        if ord(ch) in (0, 0xfffd):
            continue
        result += ch
    return result

def is_punctuation(char):
  """Checks whether `chars` is a punctuation character."""
  cp = ord(char)
  # We treat all non-letter/number ASCII as punctuation.
  # Characters such as "^", "$", and "`" are not in the Unicode
  # Punctuation class but we treat them as punctuation anyways, for
  # consistency.
  if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
      (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
    return True
  cat = unicodedata.category(char)
  if cat.startswith("P"):
    return True
  return False

def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring

def convert_to_unicode(text):
  """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
  if six.PY3:
    if isinstance(text, str):
      return text
    elif isinstance(text, bytes):
      return text.decode("utf-8", "ignore")
    else:
      raise ValueError("Unsupported string type: %s" % (type(text)))
  elif six.PY2:
    if isinstance(text, str):
      return text.decode("utf-8", "ignore")
    elif isinstance(text, unicode):
      return text
    else:
      raise ValueError("Unsupported string type: %s" % (type(text)))
  else:
    raise ValueError("Not running on Python2 or Python 3?")
