"""
Barycenter-based spelling assignment module for the Interla project.

This module assigns spellings to Interla vocabulary using string barycenter
calculations. It computes the optimal Interla orthographic representation
for each anonymous token by finding the barycenter of associated words
from multiple languages.
"""

import os
import pickle
from typing import Dict, List, Tuple

from tqdm.contrib.concurrent import process_map

from assign_spellings_common import step_1
from logging_config import logger
from str_barycenter import string_barycenter
from utils import IPA_TO_INTERLA


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

    # Access global variables (available in multiprocessing context)
    global all_y2normWord, LANG_WEIGHTS

    logger.debug(f"Computing token for anonymous token {int_anon_token}")

    # Get the words and their corresponding weights
    words: List[str] = []
    weights: List[float] = []

    for lang, w_id in assoc_words.items():
        word = all_y2normWord[lang].get(w_id, "")
        if word:  # Only include non-empty words
            words.append(word)
            weights.append(LANG_WEIGHTS[lang])

    logger.debug(f"Token {int_anon_token}: found {len(words)} valid words")

    # Compute barycenter based on number of words
    if len(words) == 0:
        logger.debug(f"No valid words for token {int_anon_token}")
        int_ipa_token = ""
    elif len(words) == 1:
        logger.debug(f"Single word for token {int_anon_token}: {words[0]}")
        int_ipa_token = words[0]
    else:
        logger.debug(f"Computing barycenter for {len(words)} words")
        try:
            int_ipa_token = string_barycenter(words, weights)
            logger.debug(f"Barycenter result: {int_ipa_token}")
        except Exception as e:
            logger.warning(
                f"Failed to compute barycenter for token {int_anon_token}: {e}"
            )
            int_ipa_token = ""

    # Convert from IPA to Interla orthography
    int_orth_token = ""
    if int_ipa_token:
        try:
            int_orth_token = "".join(
                IPA_TO_INTERLA[char] for char in int_ipa_token
            )
            logger.debug(
                f"Converted IPA '{int_ipa_token}' to orthography '{int_orth_token}'"
            )
        except Exception as e:
            logger.warning(
                f"Failed to convert IPA to orthography for token {int_anon_token}: {e}"
            )
            int_orth_token = ""

    return int_orth_token, int_anon_token


def load_or_compute_vocabulary() -> Dict[str, int]:
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

    # Access global variables
    global int_anon_tokens_coocurrences

    vocab: Dict[str, int] = {}

    try:
        logger.debug(f"Processing {len(int_anon_tokens_coocurrences)} anonymous tokens")
        results = process_map(
            compute_token,
            list(int_anon_tokens_coocurrences.items()),
            desc="Computing Interla tokens using barycenter method",
            # chunksize=1
        )

        # Process results
        empty_tokens = 0
        for int_orth_token, int_anon_token in results:
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


def display_vocabulary_sample(vocab: Dict[str, int], sample_size: int = 10) -> None:
    """
    Display a sample of the generated vocabulary.

    Args:
        vocab: The generated vocabulary dictionary
        sample_size: Number of entries to display
    """
    logger.debug(
        f"Displaying sample of {min(sample_size, len(vocab))} vocabulary entries"
    )

    vocab_items = list(vocab.items())[:sample_size]

    print("Sample Vocabulary Entries:")
    print("-" * 40)
    for i, (orth_token, anon_token) in enumerate(vocab_items, 1):
        print(f"{i:2d}. {orth_token} -> {anon_token}")

    if len(vocab) > sample_size:
        print(f"... and {len(vocab) - sample_size} more entries")


def main() -> None:
    """Main function for barycenter-based spelling assignment."""
    logger.debug("Starting barycenter-based spelling assignment")

    try:
        # Load anonymous tokens and associated data
        logger.debug("Loading anonymous tokens and language data")

        global int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS
        int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = (
            step_1()
        )

        logger.debug(f"Loaded {len(int_anon_tokens_coocurrences)} anonymous tokens")
        logger.debug(f"Loaded normalized words for {len(all_y2normWord)} languages")
        logger.debug(f"Loaded original words for {len(all_y2word)} languages")
        logger.debug(f"Loaded weights for {len(LANG_WEIGHTS)} languages")

        # Load or compute vocabulary
        vocab = load_or_compute_vocabulary()

        # Display sample results
        display_vocabulary_sample(vocab)

        logger.debug("Barycenter-based spelling assignment completed successfully")

    except Exception as e:
        logger.critical(f"Critical error in barycenter-based assignment: {e}")
        raise


if __name__ == "__main__":
    main()
