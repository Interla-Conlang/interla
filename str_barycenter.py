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

    from assign_spellings_common import IPAProcessor
    from utils import get_lang_weights

    _, LANG_WEIGHTS = get_lang_weights()
    # words = [
    #     ipa_processor.process_str(s)
    #     for s, lang in [
    #         ("lista", "es"),
    #         ("Liste", "de"),
    #         ("list", "en"),
    #         ("lista", "it"),
    #         ("cả_thảy", "vi"),
    #         ("Blacklist", "id"),
    #         ("Listede", "tr"),
    #         ("liste", "fr"),
    #         ("lista", "pt"),
    #     ]
    # ]
    # weights = [
    #     LANG_WEIGHTS[lang]
    #     for lang in ["es", "de", "en", "it", "vi", "id", "tr", "fr", "pt"]
    # ]

    # Using IPA conversion for each word with its corresponding language
    words_with_langs = [
        ("noir", "fr"),
        ("black", "en"),
        ("schwarz", "de"),
        ("negro", "es"),
        ("nero", "it"),
        ("đen", "vi"),
        ("hitam", "id"),
        ("siyah", "tr"),
        ("preto", "pt"),
    ]

    # Create IPA processors for each unique language
    unique_langs = list(set(lang for _, lang in words_with_langs))
    ipa_processors = {lang: IPAProcessor(lang) for lang in unique_langs}

    words = [ipa_processors[lang].process_str(word) for word, lang in words_with_langs]
    weights = [LANG_WEIGHTS[lang] for _, lang in words_with_langs]
    print(string_barycenter(words, weights))
