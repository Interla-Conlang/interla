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
    # print(string_barycenter(["hello", "hallo", "hola"]))
    # print(string_barycenter(["spirit", "spirito", "esprit", "gespenst"]))

    from assign_spellings_common import IPAProcessor
    from utils import get_lang_weights

    _, LANG_WEIGHTS = get_lang_weights()
    # words_with_langs = [
    #     ("lista", "es"),
    #     ("Liste", "de"),
    #     ("list", "en"),
    #     ("lista", "it"),
    #     ("cả_thảy", "vi"),
    #     ("Blacklist", "id"),
    #     ("Listede", "tr"),
    #     ("liste", "fr"),
    #     ("lista", "pt"),
    # ]

    # words_with_langs = [
    #     ("noir", "fr"),
    #     ("black", "en"),
    #     ("schwarz", "de"),
    #     ("negro", "es"),
    #     ("nero", "it"),
    #     ("đen", "vi"),
    #     ("hitam", "id"),
    #     ("siyah", "tr"),
    #     ("preto", "pt"),
    # ]

    words_with_langs = [
        ("Black", "it"),
        ("Sirius", "vi"),
        ("Sirius", "id"),
        ("Sirius", "tr"),
        ("天狼星", "zh_tw"),
        ("Sirius", "pt"),
    ]

    # Create IPA processors for each unique language
    unique_langs = list(set(lang for _, lang in words_with_langs))
    weights = [LANG_WEIGHTS[lang] for _, lang in words_with_langs]

    ipa_processors = {lang: IPAProcessor(lang, replace=False) for lang in unique_langs}

    words = [ipa_processors[lang].process_str(word) for word, lang in words_with_langs]
    print("IPA converted words:", words)

    ipa_processors = {lang: IPAProcessor(lang, replace=True) for lang in unique_langs}
    words = [ipa_processors[lang].process_str(word) for word, lang in words_with_langs]
    print("Words used in barycenter:", words)
    for line in align_words_list(words):
        print(line)
    print(string_barycenter(words, weights))
