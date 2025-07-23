"""
String barycenter utilities for the Interla project.

This module provides functionality for computing string barycenters and aligning
words using multiple sequence alignment (MSA) techniques.
"""

from collections import Counter
from typing import List, Optional, Tuple

from logging_config import logger
from msa import msa


def align_words_list(word_list: List[str]) -> List[Tuple[str, ...]]:
    """
    Align a list of words using multiple sequence alignment.

    Args:
        word_list: List of words to align

    Returns:
        List of tuples representing aligned character positions

    Raises:
        ValueError: If word_list is empty
    """
    if not word_list:
        logger.error("Empty word list provided for alignment")
        raise ValueError("word_list cannot be empty")

    logger.debug(f"Aligning {len(word_list)} words: {word_list}")

    try:
        aligned = msa(word_list)
        logger.debug(f"MSA produced {len(aligned)} aligned sequences")

        # Transpose to get columns
        aligned_transposed = list(zip(*aligned))
        logger.debug(f"Transposed alignment has {len(aligned_transposed)} positions")

        return aligned_transposed
    except Exception as e:
        logger.error(f"Failed to align words {word_list}: {e}")
        raise


def string_barycenter(words: List[str], weights: Optional[List[float]] = None) -> str:
    """
    Compute the barycenter (weighted average) of a list of aligned words.

    Args:
        words: List of words to compute barycenter for
        weights: Optional weights for each word (defaults to equal weights)

    Returns:
        Barycenter string

    Raises:
        ValueError: If words is empty or weights length doesn't match words length
    """
    if not words:
        logger.error("Empty word list provided for barycenter calculation")
        raise ValueError("words cannot be empty")

    if weights is None:
        weights = [1.0] * len(words)
        logger.debug("Using equal weights for all words")
    else:
        if len(weights) != len(words):
            logger.error(
                f"Weights length ({len(weights)}) doesn't match words length ({len(words)})"
            )
            raise ValueError("weights must have same length as words")
        logger.debug(f"Using provided weights: {weights}")

    logger.debug(f"Computing barycenter for {len(words)} words")

    try:
        # Align the words first
        aligned = align_words_list(words)
        logger.debug(f"Aligned words into {len(aligned)} positions")

        bary = ""
        for i, chars in enumerate(aligned):
            counter: Counter[str] = Counter()
            for char, weight in zip(chars, weights):
                counter[char] += weight  # type: ignore

            most_common = counter.most_common(1)[0][0]
            if most_common != "-":
                bary += most_common
                logger.debug(
                    f"Position {i}: selected '{most_common}' from {dict(counter)}"
                )
            else:
                logger.debug(f"Position {i}: skipping gap character '-'")

        logger.debug(f"Computed barycenter: '{bary}' from words {words}")
        return bary

    except Exception as e:
        logger.error(f"Failed to compute barycenter for {words}: {e}")
        raise


def main() -> None:
    """Main function for testing string barycenter functionality."""
    logger.debug("Running str_barycenter main function")

    try:
        from assign_spellings_common import IPAProcessor
        from utils import get_lang_weights

        logger.debug("Loading language weights")
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

        logger.debug(f"Testing with {len(words_with_langs)} word-language pairs")

        # Create IPA processors for each unique language
        unique_langs = list(set(lang for _, lang in words_with_langs))
        weights = [LANG_WEIGHTS[lang] for _, lang in words_with_langs]

        logger.debug(f"Creating IPA processors for languages: {unique_langs}")
        ipa_processors = {}
        for lang in unique_langs:
            try:
                ipa_processors[lang] = IPAProcessor(lang, replace=False)
            except Exception as e:
                logger.warning(f"Failed to create IPA processor for {lang}: {e}")

        # Process words without replacement
        logger.debug("Processing words without IPA replacement")
        words = []
        for word, lang in words_with_langs:
            if lang in ipa_processors:
                processed = ipa_processors[lang].process_str(word)
                words.append(processed)
            else:
                logger.warning(
                    f"No IPA processor for {lang}, using original word: {word}"
                )
                words.append(word)

        print("IPA converted words:", words)

        # Process words with replacement
        logger.debug("Processing words with IPA replacement")
        ipa_processors_replace = {}
        for lang in unique_langs:
            try:
                ipa_processors_replace[lang] = IPAProcessor(lang, replace=True)
            except Exception as e:
                logger.warning(
                    f"Failed to create replacement IPA processor for {lang}: {e}"
                )

        words_replaced = []
        for word, lang in words_with_langs:
            if lang in ipa_processors_replace:
                processed = ipa_processors_replace[lang].process_str(word)
                words_replaced.append(processed)
            else:
                logger.warning(
                    f"No replacement IPA processor for {lang}, using original: {word}"
                )
                words_replaced.append(word)

        print("Words used in barycenter:", words_replaced)

        # Display alignment
        logger.debug("Displaying word alignment")
        for line in align_words_list(words_replaced):
            print(line)

        # Compute and display barycenter
        logger.debug("Computing string barycenter")
        barycenter = string_barycenter(words_replaced, weights)
        print("Barycenter:", barycenter)

    except Exception as e:
        logger.critical(f"Critical error in main function: {e}")
        raise


if __name__ == "__main__":
    main()
