"""
Vocabulary visualization

This module provides functionality to visualize and explore the Interla vocabulary
by showing word associations across different languages with their IPA transcriptions.
"""

import os
import pickle
from typing import Dict, List

from assign_spellings_common import IPAProcessor, step_1
from constants import LANG_TO_EPITRAN
from logging_config import logger
from str_barycenter import align_words_list
from utils import ALL_VALID_LANGUAGES


def viz_vocab() -> None:
    """
    Visualize the Interla vocabulary by showing word associations across languages.

    This function loads the Interla vocabulary and displays associated words from
    different languages with their IPA transcriptions and normalized forms.

    Returns:
        None

    Raises:
        FileNotFoundError: If the Interla vocabulary file is not found
    """
    logger.info("Starting vocabulary visualization")

    logger.debug("Loading data from step_1")
    int_anon_tokens_coocurrences, all_y2normWord, all_y2word, _ = step_1()
    logger.debug(
        f"Loaded {len(int_anon_tokens_coocurrences)} anonymous token cooccurrences"
    )

    logger.debug("Initializing IPA processors for valid languages")
    ipa_processors: Dict[str, IPAProcessor] = {}
    for lang in ALL_VALID_LANGUAGES:
        if LANG_TO_EPITRAN[lang] is not None:
            ipa_processors[lang] = IPAProcessor(lang, replace=False)

    interla_vocab_path = "output/interla_vocab.pkl"
    logger.debug(f"Checking for Interla vocabulary at {interla_vocab_path}")

    if not os.path.exists(interla_vocab_path):
        logger.error(f"Interla vocabulary file not found at {interla_vocab_path}")
        return

    logger.debug("Loading Interla vocabulary")
    try:
        with open(interla_vocab_path, "rb") as f:
            vocab: Dict[str, int] = pickle.load(f)
        logger.info(f"Loaded vocabulary with {len(vocab)} entries")
    except Exception as e:
        logger.error(f"Failed to load vocabulary from {interla_vocab_path}: {e}")
        return

    for int_orth_token, int_anon_token in vocab.items():
        assoc_words = int_anon_tokens_coocurrences.get(int_anon_token, {})

        # Filter for interesting entries (more than 5 associations, includes EN or FR)
        if len(assoc_words) > 5 and ("en" in assoc_words or "fr" in assoc_words):
            print(f"Interla: {int_orth_token}")

            items = sorted(
                assoc_words.items(),
                key=lambda x: x[0],  # sort alphabetically by language code
            )

            words: List[str] = [all_y2word[lang][y_id] for lang, y_id in items]
            normWords: List[str] = [all_y2normWord[lang][y_id] for lang, y_id in items]
            ipas: List[str] = [
                ipa_processors[lang].process_str(word)
                for (lang, _), word in zip(items, words)
            ]

            # Display word information
            for word, normWord, ipa, (lang, _) in zip(
                words, normWords, ipas, items
            ):
                print(f"  {lang}:\t\t{word}\t\t/{ipa}/\t\t({normWord})")

            # Display alignment
            for line in align_words_list(normWords):
                print(" ".join(line))

            input()  # Wait for user input before showing next entry



def main() -> None:
    """Main function for running vocabulary visualization."""
    try:
        viz_vocab()
    except KeyboardInterrupt:
        logger.info("Vocabulary visualization interrupted by user")


if __name__ == "__main__":
    main()
