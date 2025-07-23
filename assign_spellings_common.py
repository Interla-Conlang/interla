"""
Abbreviations:
- et: Estonian
- int: Interla
- anon: anonymous
- orth: orthographied
"""

import glob
import os
import pickle
import unicodedata
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import epitran
import pandas as pd
from epitran.download import cedict
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from utils import get_lang_weights

cedict()  # downloads cedict

TO_KEEP = {
    "en",
    "zh_cn",
    # "hi",  # TODO: need transliteration
    "es",
    # "ar",  # TODO: need transliteration
    # "bn",  # TODO: need transliteration
    "fr",
    # "ru",  # TODO: need transliteration
    "pt",
    # "ur",  # TODO: need transliteration
    "id",
    "de",
    # "ja",  # TODO: need transliteration
    # "te",  # TODO: need transliteration
    "tr",
    # "ta",  # TODO: need transliteration
    # "ko",  # TODO: need transliteration
    "vi",
    "it",
    # "th",  # TODO: need transliteration
    "tl",
    "zh_tw",
    # "fa",  # TODO: need transliteration
    "zh_cn",
}


# Language code mapping from your TO_KEEP codes to epitran codes
LANG_TO_EPITRAN = {
    "en": "eng-Latn",
    "zh_cn": "cmn-Hans",
    "es": "spa-Latn",
    "fr": "fra-Latn",
    "pt": "por-Latn",
    "id": "ind-Latn",
    "de": "deu-Latn",
    "tr": "tur-Latn",
    "vi": "vie-Latn",
    "it": "ita-Latn",
    "tl": "tgl-Latn",
    "zh_tw": "cmn-Hant",
}

VALID_INT_IPA = set(pd.read_csv("output/alphabet.csv")["IPA"])


def load_ipa_replacement_dict(lang_code: str) -> Dict[str, str]:
    """
    Load the IPA replacement dictionary for a given language code.
    The dictionary maps characters to their IPA equivalents.
    """
    _ = lang_code  # TODO: for the moment, we ignore the language code
    df = pd.read_csv("data/closest_phonems.csv")
    # Only keep rows where lang is "*" or matches lang_code (for future extension)
    replacements = dict(zip(df["source_ipa"], df["target_ipa"]))
    return replacements


class IPAProcessor:
    """
    A processor that converts strings to IPA using epitran for a specific language.
    Initialize once per language and reuse for efficient processing.
    """

    def __init__(self, lang_code: str, replace: bool = True):
        self.lang_code = lang_code
        self.epitran_code = LANG_TO_EPITRAN[lang_code]
        self.epitran_obj = epitran.Epitran(self.epitran_code)

        if replace:
            replacement_dict = load_ipa_replacement_dict(lang_code)
            self.ipa_replace = lambda c: replacement_dict.get(c, "")
        else:
            self.ipa_replace = lambda c: c  # No replacement, keep original IPA

    def process_str(self, s):
        """
        Convert a string to IPA using epitran.
        """
        if not s:
            return s

        raw_ipa = self.epitran_obj.transliterate(s.lower())

        # Filter out invalid IPA characters
        filtered_ipa = "".join(self.ipa_replace(char) for char in raw_ipa)

        return filtered_ipa


def process_str(s):
    """
    Process a string for string comparison.
    - lowercase it
    - replace special characters (e.g. accents) with their ASCII equivalents
    """
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s


def process_chunk(lang2, chunk: List[str]) -> List[str]:
    ipa_processor = IPAProcessor(lang2)
    return [ipa_processor.process_str(word) for word in chunk]


os.makedirs("output/ipa", exist_ok=True)


def step_1(N: Optional[int] = None):
    # FIXME: ~30s long

    # 1. Load all pkl files from data/translations/downloads/xx-yy.pkl if yy is "et"
    pkl_dir = "data/translations/downloads"
    pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
    et_pkls = [
        f
        for f in pkl_files
        if os.path.basename(f).startswith("et-")
        and os.path.basename(f).split("-")[1].split(".")[0] in TO_KEEP
    ]

    # TODO: ALSO USE os.path.basename(f)[:2] == "et"

    _, LANG_WEIGHTS = get_lang_weights()
    min_weight = min(LANG_WEIGHTS.values())
    LANG_WEIGHTS = defaultdict(lambda: min_weight, LANG_WEIGHTS)

    int_anon_tokens_coocurrences = dict()  # 156: {"fi": [159, 8], "sv": [2, 8]}
    all_y2normWord = dict()  # To collect all y2word mappings
    all_y2word = dict()  # To collect all y2word mappings
    all_word2x = dict()  # To collect all word2x mappings

    for fpath in et_pkls:
        lang2 = (
            os.path.basename(fpath).split("-")[1].split(".")[0]
        )  # e.g. "fi" from "et-fi.pkl"

        with open(fpath, "rb") as f:
            word2x, y2word, x2ys = pickle.load(f)
            x2word = {
                v: k for k, v in word2x.items()
            }  # Reverse mapping: id -> word in lang1
            # word2x is a dict: word -> id in lang1
            # y2word is a dict: id -> word in lang2
            # x2ys is a dict: id in lang1 -> list of ids in lang2

        # Check if output/step1.pkl exists
        output_path = f"output/ipa/{lang2}.pkl"
        if os.path.exists(output_path):
            with open(output_path, "rb") as f:
                y2normWord = pickle.load(f)
        else:
            ipa_processor = IPAProcessor(lang2)
            if lang2 in {"en"}:
                # Use thread_map for parallel processing
                keys = list(y2word.keys())
                values = list(y2word.values())
                norm_values = thread_map(
                    ipa_processor.process_str, values, desc=f"Processing {lang2} words"
                )
                y2normWord = dict(zip(keys, norm_values))
            else:
                y2normWord = {
                    k: ipa_processor.process_str(v)
                    for k, v in tqdm(y2word.items(), desc=f"Processing {lang2} words")
                }

            # Save the processed y2normWord to a pickle file
            print(f"Saving {lang2} IPA words to {output_path}")
            with open(output_path, "wb") as f:
                pickle.dump(y2normWord, f)

        all_y2normWord[lang2] = y2normWord  # Collect all y2word mappings
        all_y2word[lang2] = y2word

        # TODO: WE ASSUME THERE ARE RANKED BY FREQUENCY
        records = list(x2ys.items())[:N] if N is not None else x2ys.items()
        for x_id, ys in records:  # Limit to N to match interla tokens
            # reindex x_id
            word = x2word.get(x_id)
            if word in all_word2x:
                new_x_id = all_word2x[word]
            else:
                new_x_id = len(all_word2x)
                all_word2x[word] = new_x_id

            int_anon_tokens_coocurrences.setdefault(new_x_id, dict())
            # int_anon_tokens_coocurrences[x_id][lang2] = ys[:3]
            int_anon_tokens_coocurrences[new_x_id][lang2] = ys[0]

    print(len(int_anon_tokens_coocurrences), "interla anonymous tokens")
    return int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS


def get_all_ipa_from_normWords(all_y2normWord: Dict[str, Dict[str, str]]) -> Counter:
    all_ipa = Counter()
    for normWords in all_y2normWord.values():
        for normWord in normWords.values():
            for letter in normWord:
                if letter not in {"-", " "}:
                    all_ipa[letter] += 1
    return all_ipa


if __name__ == "__main__":
    int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()
    all_ipa = get_all_ipa_from_normWords(all_y2normWord)
    # Show the most common IPA characters
    print("Most common IPA characters:")
    for ipa, count in all_ipa.most_common(300):
        print(f"{ipa}: {count}")
