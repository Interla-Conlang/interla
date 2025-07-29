"""
Barycenter-based spelling assignment module for the Interla project.

This module assigns spellings to Interla vocabulary using string barycenter
calculations. It computes the optimal Interla orthographic representation
for each anonymous token by finding the barycenter of associated words
from multiple languages.
"""

import os
import pickle
from typing import Dict, Tuple

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from assign_spellings_common import step_1
from logging_config import logger
from str_barycenter import string_barycenter
from utils import IPA_TO_INTERLA

# Global variables that will be initialized in each worker process
_all_y2normWord: Dict[str, Dict[int, str]] = {}
_LANG_WEIGHTS: Dict[str, float] = {}


def compute_token(args: Tuple[int, Dict[str, int]]) -> Tuple[str, int]:
    """
    Compute the Interla orthographic token for a given anonymous token.

    This function is designed for parallel processing and computes the
    barycenter of associated words from multiple languages.

    Args:
        args: Tuple containing (anonymous_token_id, associated_words_dict)
              where associated_words_dict maps language codes to word IDs

    Returns:
        Tuple containing (interla_orthographic_token, anonymous_token_id)
    """
    int_anon_token, assoc_words = args

    # Use global variables
    global _all_y2normWord, _LANG_WEIGHTS

    # Get the words and their corresponding weights
    words = []
    weights = []

    for lang, w_id in assoc_words.items():
        word = _all_y2normWord[lang].get(w_id, "")
        if word:  # Only include non-empty words
            words.append(word)
            weights.append(_LANG_WEIGHTS[lang])

    # Compute barycenter based on number of words
    if len(words) == 0:
        int_ipa_token = ""
    elif len(words) == 1:
        int_ipa_token = words[0]
    else:
        int_ipa_token = string_barycenter(words, weights, use_heuristic=True)

    # Convert from IPA to Interla orthography
    int_orth_token = ""
    if int_ipa_token:
        int_orth_token = "".join(IPA_TO_INTERLA[char] for char in int_ipa_token)

    return int_orth_token, int_anon_token


def load_or_compute_vocabulary(
    int_anon_tokens_coocurrences: Dict[int, Dict[str, int]],
    all_y2normWord: Dict[str, Dict[int, str]],
    LANG_WEIGHTS: Dict[str, float],
) -> Dict[str, int]:
    """
    Load existing vocabulary or compute it using barycenter method.

    Returns:
        Dictionary mapping Interla orthographic tokens to anonymous token IDs

    Raises:
        Exception: If computation fails
    """
    interla_vocab_path = "output/interla_vocab.pkl"

    if os.path.exists(interla_vocab_path):
        logger.debug(f"Loading existing vocabulary from {interla_vocab_path}")
        try:
            with open(interla_vocab_path, "rb") as f:
                vocab: Dict[str, int] = pickle.load(f)
            logger.debug(f"Loaded vocabulary with {len(vocab)} entries")
            return vocab
        except Exception as e:
            logger.error(f"Failed to load existing vocabulary: {e}")
            raise

    logger.debug("Computing new vocabulary using barycenter method")

    vocab: Dict[str, int] = {}

    try:
        logger.debug(f"Processing {len(int_anon_tokens_coocurrences)} anonymous tokens")

        items_list = list(int_anon_tokens_coocurrences.items())

        # Set global variables for the current process (will be inherited by workers)
        global _all_y2normWord, _LANG_WEIGHTS
        _all_y2normWord = all_y2normWord
        _LANG_WEIGHTS = LANG_WEIGHTS

        cpu_count = os.cpu_count() or 4
        max_workers = min(cpu_count, 1)  # Problem is that I'm bound by memory
        chunksize = max(1, len(items_list) // (max_workers * 50))

        # Process all items and handle results incrementally to avoid memory buildup
        vocab: Dict[str, int] = {}
        empty_tokens = 0

        # Process results as they come in instead of storing them all
        for int_orth_token, int_anon_token in (
            process_map(
                compute_token,
                items_list,
                desc="Computing Interla tokens using barycenter method",
                max_workers=max_workers,
                chunksize=chunksize,
            )
            if max_workers > 1
            else tqdm(
                map(compute_token, items_list),
                total=len(items_list),
                desc="Computing Interla tokens using barycenter method",
            )
        ):
            if int_orth_token:  # Only include non-empty tokens
                vocab[int_orth_token] = int_anon_token
            else:
                empty_tokens += 1

        logger.debug(f"Generated {len(vocab)} valid vocabulary entries")
        if empty_tokens > 0:
            logger.warning(f"Skipped {empty_tokens} empty tokens")

        # Save the vocabulary to a pickle file
        logger.debug(f"Saving vocabulary to {interla_vocab_path}")
        with open(interla_vocab_path, "wb") as f:
            pickle.dump(vocab, f)
        logger.debug("Vocabulary saved successfully")

    except Exception as e:
        logger.error(f"Failed to compute vocabulary: {e}")
        raise

    return vocab


def main() -> None:
    """Main function for barycenter-based spelling assignment."""
    logger.debug("Starting barycenter-based spelling assignment")

    try:
        # Load anonymous tokens and associated data
        logger.debug("Loading anonymous tokens and language data")

        int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = (
            step_1()
        )

        logger.debug(f"Loaded {len(int_anon_tokens_coocurrences)} anonymous tokens")
        logger.debug(f"Loaded normalized words for {len(all_y2normWord)} languages")
        logger.debug(f"Loaded original words for {len(all_y2word)} languages")
        logger.debug(f"Loaded weights for {len(LANG_WEIGHTS)} languages")

        # Load or compute vocabulary
        load_or_compute_vocabulary(
            int_anon_tokens_coocurrences, all_y2normWord, LANG_WEIGHTS
        )

        logger.debug("Barycenter-based spelling assignment completed successfully")

    except Exception as e:
        logger.critical(f"Critical error in barycenter-based assignment: {e}")
        raise


if __name__ == "__main__":
    main()
