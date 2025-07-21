"""
Some tests around the notion of barycenter for strings.
"""

from collections import Counter
from typing import List, Tuple

from Levenshtein import opcodes


def align_pair(w1, w2):
    aligned1, aligned2 = [], []
    for tag, i1, i2, j1, j2 in opcodes(w1, w2):
        if tag == "equal":
            aligned1.extend(w1[i1:i2])
            aligned2.extend(w2[j1:j2])
        elif tag == "replace":
            for a, b in zip(w1[i1:i2], w2[j1:j2]):
                aligned1.append(a)
                aligned2.append(b)
        elif tag == "insert":
            aligned1.extend(["-"] * (j2 - j1))
            aligned2.extend(w2[j1:j2])
        elif tag == "delete":
            aligned1.extend(w1[i1:i2])
            aligned2.extend(["-"] * (i2 - i1))
    return aligned1, aligned2


# progressive alignment
def align_words_list(word_list: List[str]) -> List[Tuple[str, ...]]:
    aligned = list(word_list[:2])
    a1, a2 = align_pair(*aligned)
    aligned = [a1, a2]
    for w in word_list[2:]:
        new_aligned = []
        for seq in aligned:
            a_old, a_new = align_pair("".join(seq), w)
            new_aligned.append(a_old)
            w = "".join(a_new)
        aligned = new_aligned + [list(w)]
    return list(zip(*aligned))


def string_barycenter(words: List[str]) -> str:
    # Align the words first
    aligned = align_words_list(words)
    bary = ""
    for chars in aligned:
        most_common = Counter(chars).most_common(1)[0][0]
        if most_common != "-":
            bary += most_common
    return bary


if __name__ == "__main__":
    # Output
    for line in align_words_list(["esprit", "spirit", "spirito", "gespenst"]):
        print(line)

    print(string_barycenter(["hello", "hallo", "hola"]))
    print(string_barycenter(["spirit", "spirito", "esprit", "gespenst"]))
