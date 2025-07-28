"""
Common code for assigning spellings.

This module provides common functionalities for processing and assigning spellings
to words (barycenter or other methods).

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
from typing import Dict, List, Optional, Tuple

import epitran
import pandas as pd
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from constants import LANG_TO_EPITRAN
from logging_config import logger
from utils import get_lang_weights

# logger.debug("Downloading cedict data")
# from epitran.download import cedict
# cedict()  # downloads cedict

TO_KEEP = set([k for k, v in LANG_TO_EPITRAN.items() if v is not None])
logger.debug(f"Languages to keep: {len(TO_KEEP)} languages")


def load_ipa_replacement_dict(lang_code: str) -> Dict[str, str]:
    """
    Load the IPA replacement dictionary for a given language code.

    The dictionary maps characters to their IPA equivalents. Currently ignores
    the language code and uses a universal replacement mapping.

    Args:
        lang_code: Language code (currently unused but kept for future extension)

    Returns:
        Dictionary mapping source IPA characters to target IPA characters

    Raises:
        FileNotFoundError: If closest_phonems.csv is not found
    """
    logger.debug(f"Loading IPA replacement dictionary for language: {lang_code}")
    _ = lang_code  # TODO: for the moment, we ignore the language code

    df = pd.read_csv("data/closest_phonems.csv")
    logger.debug(f"Loaded {len(df)} IPA replacement mappings")

    # Only keep rows where lang is "*" or matches lang_code (for future extension)
    replacements = dict(zip(df["source_ipa"], df["target_ipa"]))
    logger.debug(f"Created {len(replacements)} IPA replacement mappings")
    return replacements


class IPAProcessor:
    """
    A processor that converts strings to IPA using epitran for a specific language.

    This class provides efficient IPA processing by initializing epitran once per
    language and reusing it for multiple string conversions.

    Attributes:
        lang_code: The language code for this processor
        epitran_code: The epitran language code
        epitran_obj: The epitran processor instance
        ipa_replace: Function to replace IPA characters
    """

    def __init__(self, lang_code: str, replace: bool = True) -> None:
        """
        Initialize the IPA processor for a specific language.

        Args:
            lang_code: Language code (e.g., 'en', 'fr', 'de')
            replace: Whether to apply IPA character replacements

        Raises:
            KeyError: If lang_code is not found in LANG_TO_EPITRAN
            ValueError: If epitran_code is None for the given language
        """
        self.lang_code = lang_code
        logger.debug(f"Initializing IPA processor for language: {lang_code}")

        if lang_code not in LANG_TO_EPITRAN:
            logger.error(f"Language code {lang_code} not found in LANG_TO_EPITRAN")
            raise KeyError(f"Language code {lang_code} not supported")

        self.epitran_code = LANG_TO_EPITRAN[lang_code]
        if self.epitran_code is None:
            logger.error(f"No epitran code available for language {lang_code}")
            raise ValueError(f"No epitran support for language {lang_code}")

        try:
            self.epitran_obj = epitran.Epitran(self.epitran_code)
            logger.debug(f"Successfully initialized epitran for {self.epitran_code}")
        except Exception as e:
            logger.error(f"Failed to initialize epitran for {self.epitran_code}: {e}")
            raise

        if replace:
            logger.debug("Loading IPA replacement dictionary")
            replacement_dict = load_ipa_replacement_dict(lang_code)
            self.ipa_replace = lambda c: replacement_dict.get(c, "")
        else:
            logger.debug("No IPA replacement will be applied")
            self.ipa_replace = lambda c: c  # No replacement, keep original IPA

    def process_str(self, s: str) -> str:
        """
        Convert a string to IPA using epitran.

        Args:
            s: Input string to convert to IPA

        Returns:
            IPA transcription of the input string
        """
        if not s:
            logger.debug("Empty string provided, returning as-is")
            return s

        try:
            raw_ipa = self.epitran_obj.transliterate(s.lower())
            logger.debug(f"Raw IPA for '{s}': {raw_ipa}")

            # Filter out invalid IPA characters
            filtered_ipa = "".join(self.ipa_replace(char) for char in raw_ipa)
            logger.debug(f"Filtered IPA: {filtered_ipa}")

            return filtered_ipa
        except Exception as e:
            logger.warning(f"Failed to process string '{s}': {e}")
            return ""


def process_str(s: str) -> str:
    """
    Process a string for string comparison.

    This function normalizes strings by:
    - Converting to lowercase
    - Replacing special characters (e.g. accents) with their ASCII equivalents
    - Removing combining characters

    Args:
        s: Input string to process

    Returns:
        Normalized string
    """
    logger.debug(f"Processing string: '{s}'")
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    logger.debug(f"Processed result: '{s}'")
    return s


def process_chunk(lang2: str, chunk: List[str]) -> List[str]:
    """
    Process a chunk of words for a specific language using IPA conversion.

    Args:
        lang2: Language code for the chunk
        chunk: List of words to process

    Returns:
        List of IPA-processed words
    """
    logger.debug(f"Processing chunk of {len(chunk)} words for language {lang2}")
    ipa_processor = IPAProcessor(lang2)
    results = [ipa_processor.process_str(word) for word in chunk]
    logger.debug(f"Successfully processed {len(results)} words")
    return results


# Ensure output directory exists
os.makedirs("output/ipa", exist_ok=True)


def step_1(
    N: Optional[int] = None,
) -> Tuple[
    Dict[int, Dict[str, int]],
    Dict[str, Dict[int, str]],
    Dict[str, Dict[int, str]],
    Dict[str, float],
]:
    """
    Load and process translation data from pickle files.

    This function performs the first step of the pipeline by:
    1. Loading translation pickle files
    2. Processing words through IPA conversion
    3. Building cooccurrence mappings
    4. Caching processed results

    Args:
        N: Optional limit on number of records to process per language

    Returns:
        Tuple containing:
            - int_anon_tokens_coocurrences: Mapping of token IDs to language-word associations
            - all_y2normWord: Mapping of language to word ID to normalized word
            - all_y2word: Mapping of language to word ID to original word
            - LANG_WEIGHTS: Language weights dictionary

    Raises:
        FileNotFoundError: If required data files are not found
    """
    logger.debug("Starting step_1 data processing")
    # FIXME: ~30s long

    # 1. Load all pkl files from data/translations/downloads/xx-yy.pkl if yy is "et"
    pkl_dir = "data/translations/downloads"
    logger.debug(f"Scanning for pickle files in {pkl_dir}")
    pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
    et_pkls = [
        f
        for f in pkl_files
        if os.path.basename(f).startswith("et-")
        and os.path.basename(f).split("-")[1].split(".")[0] in TO_KEEP
    ]
    logger.debug(f"Found {len(et_pkls)} Estonian translation files to process")

    # TODO: ALSO USE os.path.basename(f)[:2] == "et"

    logger.debug("Loading language weights")
    _, LANG_WEIGHTS = get_lang_weights()
    min_weight = min(LANG_WEIGHTS.values())
    LANG_WEIGHTS = defaultdict(lambda: min_weight, LANG_WEIGHTS)
    logger.debug(f"Loaded weights for {len(LANG_WEIGHTS)} languages")

    logger.debug("Initializing data structures")
    int_anon_tokens_coocurrences: Dict[
        int, Dict[str, int]
    ] = {}  # 156: {"fi": [159, 8], "sv": [2, 8]}
    all_y2normWord: Dict[str, Dict[int, str]] = {}  # To collect all y2word mappings
    all_y2word: Dict[str, Dict[int, str]] = {}  # To collect all y2word mappings
    all_word2x: Dict[str, int] = {}  # To collect all word2x mappings

    for fpath in et_pkls:
        lang2 = (
            os.path.basename(fpath).split("-")[1].split(".")[0]
        )  # e.g. "fi" from "et-fi.pkl"
        logger.debug(f"Processing language: {lang2}")

        try:
            with open(fpath, "rb") as f:
                word2x, y2word, x2ys = pickle.load(f)
                x2word = {
                    v: k for k, v in word2x.items()
                }  # Reverse mapping: id -> word in lang1
                # word2x is a dict: word -> id in lang1
                # y2word is a dict: id -> word in lang2
                # x2ys is a dict: id in lang1 -> list of ids in lang2
            logger.debug(f"Loaded {len(y2word)} words for {lang2}")
        except Exception as e:
            logger.error(f"Failed to load pickle file {fpath}: {e}")
            continue

        # Check if output/step1.pkl exists
        output_path = f"output/ipa/{lang2}.pkl"
        if os.path.exists(output_path):
            logger.debug(f"Loading cached IPA data for {lang2}")
            try:
                with open(output_path, "rb") as f:
                    y2normWord = pickle.load(f)
                logger.debug(f"Loaded {len(y2normWord)} cached IPA words for {lang2}")
            except Exception as e:
                logger.error(f"Failed to load cached IPA data for {lang2}: {e}")
                continue
        else:
            logger.debug(f"Processing IPA conversion for {lang2}")
            try:
                ipa_processor = IPAProcessor(lang2)
                if lang2 in {"en"}:
                    # Use thread_map for parallel processing
                    logger.debug(f"Using parallel processing for {lang2}")
                    keys = list(y2word.keys())
                    values = list(y2word.values())
                    norm_values = thread_map(
                        ipa_processor.process_str,
                        values,
                        desc=f"Processing {lang2} words",
                    )
                    y2normWord = dict(zip(keys, norm_values))
                else:
                    y2normWord = {
                        k: ipa_processor.process_str(v)
                        for k, v in tqdm(
                            y2word.items(), desc=f"Processing {lang2} words"
                        )
                    }

                # Save the processed y2normWord to a pickle file
                logger.debug(f"Saving {lang2} IPA words to {output_path}")
                with open(output_path, "wb") as f:
                    pickle.dump(y2normWord, f)
                logger.debug(
                    f"Successfully saved {len(y2normWord)} IPA words for {lang2}"
                )
            except Exception as e:
                logger.error(f"Failed to process IPA for {lang2}: {e}")
                continue

        all_y2normWord[lang2] = y2normWord  # Collect all y2word mappings
        all_y2word[lang2] = y2word

        # TODO: WE ASSUME THERE ARE RANKED BY FREQUENCY
        records = list(x2ys.items())[:N] if N is not None else x2ys.items()
        for x_id, ys in records:  # Limit to N to match interla tokens
            # reindex x_id
            word = x2word.get(x_id)
            if word is None:
                logger.warning(f"No word found for x_id {x_id} in {lang2}")
                continue

            if word in all_word2x:
                new_x_id = all_word2x[word]
            else:
                new_x_id = len(all_word2x)
                all_word2x[word] = new_x_id

            int_anon_tokens_coocurrences.setdefault(new_x_id, {})
            # int_anon_tokens_coocurrences[x_id][lang2] = ys[:3]
            int_anon_tokens_coocurrences[new_x_id][lang2] = ys[0]

    return int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS


def get_all_ipa_from_normWords(all_y2normWord: Dict[str, Dict[int, str]]) -> Counter:
    """
    Extract all IPA characters from normalized words across all languages.

    Args:
        all_y2normWord: Mapping of language to word ID to normalized word

    Returns:
        Counter of IPA characters with their frequencies
    """
    logger.debug("Extracting IPA characters from normalized words")
    all_ipa = Counter()

    for normWords in all_y2normWord.values():
        for normWord in normWords.values():
            for letter in normWord:
                if letter not in {"-", " "}:
                    all_ipa[letter] += 1

    return all_ipa


def main() -> None:
    try:
        _, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()
        all_ipa = get_all_ipa_from_normWords(all_y2normWord)

        # Show the most common IPA characters
        logger.debug("Most common IPA characters:")
        for ipa, count in all_ipa.most_common(300):
            print(f"{ipa}: {count}")
    except Exception as e:
        logger.critical(f"Critical error in main function: {e}")
        raise


if __name__ == "__main__":
    main()
