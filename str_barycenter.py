"""
Some tests around the notion of barycenter for strings.
"""

from collections import Counter
from typing import List, Optional, Tuple

from pyfamsa import Aligner, Sequence

# from Levenshtein import opcodes

# def align_pair(w1, w2):
#     aligned1, aligned2 = [], []
#     for tag, i1, i2, j1, j2 in opcodes(w1, w2):
#         if tag == "equal":
#             aligned1.extend(w1[i1:i2])
#             aligned2.extend(w2[j1:j2])
#         elif tag == "replace":
#             for a, b in zip(w1[i1:i2], w2[j1:j2]):
#                 aligned1.append(a)
#                 aligned2.append(b)
#         elif tag == "insert":
#             aligned1.extend(["-"] * (j2 - j1))
#             aligned2.extend(w2[j1:j2])
#         elif tag == "delete":
#             aligned1.extend(w1[i1:i2])
#             aligned2.extend(["-"] * (i2 - i1))
#     return aligned1, aligned2


# progressive alignment
# def align_words_list(word_list: List[str]) -> List[Tuple[str, ...]]:
#     aligned = list(word_list[:2])
#     a1, a2 = align_pair(*aligned)
#     aligned = [a1, a2]
#     for w in word_list[2:]:
#         new_aligned = []
#         for seq in aligned:
#             a_old, a_new = align_pair("".join(seq), w)
#             new_aligned.append(a_old)
#             w = "".join(a_new)
#         aligned = new_aligned + [list(w)]
#     return list(zip(*aligned))


def align_words_list(word_list: List[str]) -> List[Tuple[str, ...]]:
    # Use index as id to avoid duplicates and keep order
    sequences = [Sequence(str(i).encode(), w.encode()) for i, w in enumerate(word_list)]
    aligner = Aligner(guide_tree="upgma")
    msa = aligner.align(sequences)

    # Collect aligned sequences in order
    aligned_seqs: List[Optional[str]] = [None] * len(word_list)
    for seq in msa:
        idx = int(seq.id.decode())
        aligned_seqs[idx] = seq.sequence.decode()

    # Transpose to get columns
    return list(zip(*aligned_seqs))


def string_barycenter(words: List[str], weights: Optional[List[float]] = None) -> str:
    if weights is None:
        weights = [1.0] * len(words)
    # Align the words first
    aligned = align_words_list(words)
    bary = ""
    for chars in aligned:
        counter = Counter()
        for char, weight in zip(chars, weights):
            counter[char] += weight  # type: ignore
        most_common = counter.most_common(1)[0][0]
        if most_common != "-":
            bary += most_common
    return bary


if __name__ == "__main__":
    # *** TESTS ***
    # for line in align_words_list(["esprit", "spirit", "spirito", "gespenst"]):
    #     print(line)

    # print(string_barycenter(["hello", "hallo", "hola"]))
    # print(string_barycenter(["spirit", "spirito", "esprit", "gespenst"]))

    from assign_spellings_common import process_str
    from utils import get_lang_weights

    _, LANG_WEIGHTS = get_lang_weights()
    words = [
        process_str(s)
        for s in [
            "lista",  # es
            "Liste",  # de
            "list",  # en
            "lista",  # it
            "cả_thảy",  # vi
            "Blacklist",  # id
            "Listede",  # tr
            "liste",  # fr
            "lista",  # pt
        ]
    ]
    weights = [
        LANG_WEIGHTS[lang]
        for lang in ["es", "de", "en", "it", "vi", "id", "tr", "fr", "pt"]
    ]
    print(string_barycenter(words, weights))
