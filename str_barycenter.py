"""
String barycenter utilities for the Interla project.

This module provides functionality for computing string barycenters and aligning
words using multiple sequence alignment (MSA) techniques.
"""

from collections import Counter
from typing import List, Optional, Tuple

from gen_vocabulary import path_pronounciability_weight
from logging_config import logger
from msa import msa
from sampler import sample_tokens
from utils import LANG_WEIGHTS


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


def most_common_bary(counter: Counter[str]) -> str:
    most_common = counter.most_common(1)[0][0]
    if most_common != "-":
        return most_common
    else:
        return ""


HEURISTICS = [(3, 0.05), (5, 0.01), (7, 0.0)]
# HEURISTICS = [(3, 0.05), (7, 0.01), (15, 0.0), False]


def string_barycenter(
    words: List[str], weights: Optional[List[float]] = None, use_heuristic: bool = False
) -> str:
    """
    Compute the barycenter (weighted average) of a list of aligned words.

    Args:
        words: List of words to compute barycenter for
        weights: Optional weights for each word (defaults to equal weights)
        use_heuristic: If True, uses a heuristic to gain time

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

    # Align the words first
    aligned = align_words_list(words)
    logger.debug(f"Aligned words into {len(aligned)} positions")

    bary = ""
    tokens = []
    token_weights = []

    # TODO: the best would be to avoid introducing impossible path because of the heuristic
    def compute_bary(aligned, weights, heuristic):
        nonlocal tokens, token_weights
        tokens = []
        token_weights = []
        for chars in aligned:
            counter: Counter[str] = Counter()
            for char, weight in zip(chars, weights):
                counter[char] += weight  # type: ignore

            if heuristic:
                n, min_val = heuristic
                most_common = counter.most_common(n)
                chars_ = [most_common[0][0]]
                weights_ = [1 - most_common[0][1]]
                for char, val in most_common[1:]:
                    if val > min_val:
                        chars_.append(char)
                        weights_.append(1 - val)
                tokens.append(chars_)
                token_weights.append(weights_)
            else:
                tokens.append(list(counter.keys()))
                token_weights.append([1 - val for val in counter.values()])
        return sample_tokens(tokens, token_weights, path_pronounciability_weight)

    bary = ""
    for heuristic in HEURISTICS:
        try:
            bary = compute_bary(aligned, weights, heuristic)
            break
        except Exception as e:
            if heuristic:
                logger.warning(
                    f"Heuristic barycenter failed with heuristic {heuristic} and error: {e}. Trying next heuristic."
                )
            else:
                logger.error(f"Failed to compute barycenter without heuristic: {e}")

    logger.debug(f"Computed barycenter: '{bary}' from words {words}")

    # assert bary != ""
    return bary


def main() -> None:
    """Main function for testing string barycenter functionality."""
    logger.debug("Running str_barycenter main function")

    try:
        from assign_spellings_common import IPAProcessor

        logger.debug("Loading language weights")

        for words_with_langs in [
            [
                ("lista", "es"),
                ("Liste", "de"),
                ("list", "en"),
                ("lista", "it"),
                ("cả_thảy", "vi"),
                ("Blacklist", "id"),
                ("Listede", "tr"),
                ("liste", "fr"),
                ("lista", "pt"),
            ],
            [
                ("noir", "fr"),
                ("black", "en"),
                ("schwarz", "de"),
                ("negro", "es"),
                ("nero", "it"),
                ("đen", "vi"),
                ("hitam", "id"),
                ("siyah", "tr"),
                ("preto", "pt"),
            ],
            [
                ("Black", "it"),
                ("Sirius", "vi"),
                ("Sirius", "id"),
                ("Sirius", "tr"),
                ("天狼星", "zh_tw"),
                ("Sirius", "pt"),
            ],
        ]:
            logger.debug(f"Testing with {len(words_with_langs)} word-language pairs")

            # Create IPA processors for each unique language
            unique_langs = list(set(lang for _, lang in words_with_langs))
            weights = [LANG_WEIGHTS[lang] for _, lang in words_with_langs]

            logger.debug(f"Creating IPA processors for languages: {unique_langs}")
            ipa_processors = {}
            for lang in unique_langs:
                try:
                    ipa_processors[lang] = IPAProcessor(
                        lang, replace=False
                    )  # 49% of the time is spent creating the IPAProcessors
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
                    ipa_processors_replace[lang] = IPAProcessor(
                        lang, replace=True
                    )  # 49% of the time is spent creating the IPAProcessors
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
