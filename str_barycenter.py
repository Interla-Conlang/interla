"""
Some tests around the notion of barycenter for strings.
"""

from collections import Counter
from typing import List, Optional, Tuple

from msa import msa


def align_words_list(word_list: List[str]) -> List[Tuple[str, ...]]:
    aligned = msa(word_list)

    # Transpose to get columns
    aligned_transposed = list(zip(*aligned))
    return aligned_transposed


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
    # words = [
    #     process_str(s)
    #     for s in [
    #         "lista",  # es
    #         "Liste",  # de
    #         "list",  # en
    #         "lista",  # it
    #         "cả_thảy",  # vi
    #         "Blacklist",  # id
    #         "Listede",  # tr
    #         "liste",  # fr
    #         "lista",  # pt
    #     ]
    # ]
    # weights = [
    #     LANG_WEIGHTS[lang]
    #     for lang in ["es", "de", "en", "it", "vi", "id", "tr", "fr", "pt"]
    # ]
    words = [
        process_str(s)
        for s in [
            "noir",
            "black",
            "schwarz",
            "negro",
            "nero",
            "đen",
            "hitam",
            "siyah",
            "noir",
            "preto",
        ]
    ]
    weights = [
        LANG_WEIGHTS[lang]
        for lang in ["fr", "en", "de", "es", "it", "vi", "id", "tr", "pt"]
    ]
    print(string_barycenter(words, weights))
