"""
Some tests around the notion of barycenter for strings.
"""

from collections import Counter


def string_barycenter(words):
    max_len = max(len(w) for w in words)
    bary = ""
    for i in range(max_len):
        chars = [w[i] for w in words if i < len(w)]
        most_common = Counter(chars).most_common(1)[0][0]
        bary += most_common
    return bary


# print(string_barycenter(["hello", "hallo", "hola"]))
# TODO: would require aligning the strings first (because for example the "a" in hola should be aligned with the "o" in "hello" and "hallo", not the "l")

from Levenshtein import opcodes


def align_words(w1, w2):
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
            aligned1.extend([None] * (j2 - j1))
            aligned2.extend(w2[j1:j2])
        elif tag == "delete":
            aligned1.extend(w1[i1:i2])
            aligned2.extend([None] * (i2 - i1))
    return aligned1, aligned2


a, b = align_words("spirit", "esprit")
print(list(zip(a, b)))

a, b = align_words("spirit", "espiritu")
print(list(zip(a, b)))
