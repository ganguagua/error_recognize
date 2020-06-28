
import tools
import sys
import random
from pypinyin import pinyin, Style
import math
import json
import tokenization
import multiprocessing


frequency = [0]*50000

white_tag = ["PER", "ORG", "LOC", "nw", "nz"]
def parse_lac_result(lac_result_str):
    lac_result = eval(lac_result_str)
    tags = lac_result["tag"]
    words = lac_result["word"]
    mask = []
    left = right = 0
    for index in range(len(tags)):
        right = left + len(words[index])
        if tags[index] in white_tag:
            mask.append((left, right))
        left = right
    return mask

def load_data(file_path):
    sentences = []
    masks = []
    characters = []
    for line in open(file_path, "r").readlines():
        fields = line.strip().split('\t')
        sentence = fields[0]
        sentences.append(sentence.strip())
        mask = []
        if len(fields) > 1:
            mask = parse_lac_result(fields[1])

        masks.append(mask)
        for ch in sentence:
            if tools.is_chinese(ch) == False:
                continue
            frequency[ord(ch)-0x4e00] += 1
    #3000常用汉字
    freq_val = []
    for index in range(len(frequency)):
        k = frequency[index]
        if k > 0:
            characters.append(chr(index+0x4e00))
            freq_val.append(k)
    freq_val.sort(reverse=True)
    threshold = freq_val[1000]
    for k in range(len(frequency)):
        if frequency[k] > threshold:
            frequency[k] = threshold

    return sentences, masks, characters

after = {}
before = {}
def load_words(file_path):
    global after, before
    for line in open(file_path).readlines():
        word = line.strip()
        for index in range(1, len(word)):
            ch = word[index]
            collect = []
            if ch in before:
                collect = before[ch]
            if word[index-1] not in collect:
                collect.append(word[index-1])
                before[ch] = collect
        for index in range(0, len(word)-1):
            ch = word[index]
            collect = []
            if ch in after:
                collect = after[ch]
            if word[index+1] not in collect:
                collect.append(word[index+1])
                after[ch] = collect

def similar(ch, prefix, suffix):
    if tools.is_chinese(ch)==False:
        return ""
    res = pinyin(ch, style=Style.TONE3, heteronym=False)
    pys = []
    for item in res:
        for py in item:
            if tools.is_chinese(py)==False and py not in pys:
                pys.append(py)
    if len(pys) == 0:
        return ""
    if len(pys) == 1:
        py = pys[0]
    else:
        py = pys[random.randint(0, len(pys)-1)]
    sim_set = similar_pinyin[py]
    t = list(zip(*sim_set))
    pys = t[0]
    distances = t[1]
    index = tools.random_choice(distances)
    sim_py = pys[index]
    chs = pinyin2chs[sim_py]
    chs = remove(chs, ch)
    if len(chs) == 0:
        return ""
    return choose_by_frequency(chs, prefix, suffix)

def remove(collection, target):
    result = []
    for item in collection:
        if item == target:
            continue
        result.append(item)
    return result

def choose_by_frequency(characters, prefix, suffix):
    high_risk = []
    if prefix in after:
        high_risk.extend(after[prefix])
    if suffix in before:
        high_risk.extend(before[suffix])
    freqs = []
    for ch in characters:
        bonus = 1
        if ch in high_risk:
            bonus = 2
        freqs.append(frequency[ord(ch)-0x4e00]*bonus)
        
    index = tools.random_choice(freqs)
    return characters[index]

def is_masked(mask, pos):
    for left, right in mask:
        if pos >= left and pos < right:
            return True
    return False

white_list = ["他", "她", "它"]
def replace(sentence, mask):
    tokens = tokenizer.tokenize(sentence)
    origin_index = []
    last_index = 0
    for index in range(len(tokens)):
        if tokens[index].startswith("##"):
            tokens[index] = tokens[index][2:]
        if tokens[index] == "[UNK]":
            tokens[index] = sentence[last_index]
        origin_index.append(last_index)
        last_index += len(tokens[index])
    #sentence = tokens
    if len(tokens) == 0:
        return "", -1
    position = min(int(math.floor(random.random() * len(tokens))),len(tokens)-1)
    if is_masked(mask, origin_index[position]):
        return ("".join(tokens), -1)
    prefix = ""
    suffix = ""
    if position > 0:
        prefix = tokens[position-1]
    if position < len(tokens)-1:
        suffix = tokens[position+1]
    sim_ch = similar(tokens[position], prefix, suffix)
    #print(sentence, sim_ch, sentence[position])
    if sim_ch == "" or sim_ch in white_list or sim_ch == tokens[position]:
        return ("".join(tokens), -1)
    tokens[position] = sim_ch
    return ("".join(tokens), position)

def build_similar_set(phonetics):
    similar_pinyin = {}
    for a in phonetics:
        sim_set = []
        for b in phonetics:
            dis = tools.pinyin_distance(a, b)
            if dis < 10:
                sim_set.append((b, 1/(dis+1)))
        similar_pinyin[a] = sim_set
    return similar_pinyin

def generate_set(characters):
    pinyin2chs = {}
    for ch in characters:
        pys = pinyin(ch, style=Style.TONE3, heteronym=False)
        for item in pys:
            for py in item:
                if py not in pinyin2chs:
                    pinyin2chs[py] = [ch]
                else:
                    pinyin2chs[py].append(ch)
    return pinyin2chs

pinyin2chs = {}
similar_pinyin = {}
tokenizer = tokenization.FullTokenizer("./vocab.txt")

def main():
    global pinyin2chs,similar_pinyin
    sentences, masks, characters = load_data(sys.argv[1])
    load_words("./words")
    pinyin2chs = generate_set(characters)
    similar_pinyin = build_similar_set(pinyin2chs.keys())
    for index in range(len(sentences)):
        sentence = sentences[index]
        mask = masks[index]
        new_sentence, position = replace(sentence, mask)
        if len(new_sentence) > 0:
            print(new_sentence, position, sep="\t")

if __name__ == "__main__":
    main()
