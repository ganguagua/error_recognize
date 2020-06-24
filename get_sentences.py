
import tools
import sys

if __name__ == "__main__":
    for line in open(sys.argv[1], "r").readlines():
        line = tools.format_white_space(line)
        line = tools.strQ2B(line)
        line = tools.remove_control_character(line)
        sentences = tools.chapter_to_sentences(line.strip())
        sentences = tools.gather_sentences(sentences)
        for sentence in sentences:
            s = tools.strip_punctuation(sentence)
            if len(s) > 1 and tools.have_chinese(s):
                print(s)
