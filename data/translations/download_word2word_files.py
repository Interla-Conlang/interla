"""
Word2Word translation files downloader for the Interla project.

This module downloads word-to-word translation dictionaries from the
Kakao Brain word2word dataset for use in the Interla language generation process.
"""

import os
import sys
from collections import Counter
from typing import List, Optional, Tuple

import requests
from tqdm.contrib.concurrent import thread_map

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from logging_config import logger


def get_download_url(lang1: str, lang2: str) -> str:
    """
    Generate the download URL for a language pair.

    Args:
        lang1: First language code
        lang2: Second language code

    Returns:
        Download URL for the language pair
    """
    return f"https://mk.kakaocdn.net/dn/kakaobrain/word2word/{lang1}-{lang2}.pkl"


# Set of invalid language codes that should be skipped
INVALID_LANGUAGES = {
    "ze_en"  # Not a valid language (https://linguistics.stackexchange.com/a/35446)
}


def download_pkl(
    pair: Tuple[str, str], save_dir: str = "data/translations/downloads"
) -> None:
    """
    Download a translation dictionary file for a language pair.

    Args:
        pair: Tuple of (lang1, lang2) language codes
        save_dir: Directory to save downloaded files
    """
    lang1, lang2 = pair

    # Only download pairs that include Estonian ("et")
    if lang1 != "et" and lang2 != "et":
        logger.debug(f"Skipping pair {lang1}-{lang2} (no Estonian)")
        return

    # Skip invalid languages
    if lang1 in INVALID_LANGUAGES or lang2 in INVALID_LANGUAGES:
        logger.warning(f"Skipping invalid language pair: {lang1}-{lang2}")
        return

    url = get_download_url(lang1, lang2)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{lang1}-{lang2}.pkl")

    # Skip if file already exists
    if os.path.exists(save_path):
        logger.debug(f"File {save_path} already exists. Skipping download.")
        return

    logger.debug(f"Downloading {url}")

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                logger.debug(f"Successfully saved to {save_path}")
                return
            else:
                logger.error(
                    f"Failed to download {url} (status code: {response.status_code})"
                )
                return

        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
        ) as e:
            logger.warning(
                f"Download failed (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt == max_retries - 1:
                logger.error(f"Giving up on {url} after {max_retries} attempts")

        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Giving up on {url} after {max_retries} attempts")
                return


def load_language_pairs(filepath: str) -> List[Tuple[str, str]]:
    """
    Load language pairs from the supporting languages file.

    Args:
        filepath: Path to the supporting languages file

    Returns:
        List of (lang1, lang2) tuples

    Raises:
        FileNotFoundError: If the supporting languages file is not found
    """
    logger.debug(f"Loading language pairs from {filepath}")

    pairs = []
    try:
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                pair = line.strip()
                if not pair or "-" not in pair:
                    continue

                parts = pair.split("-")
                if len(parts) != 2:
                    logger.warning(f"Invalid pair format on line {line_num}: {pair}")
                    continue

                lang1, lang2 = parts
                pairs.append((lang1, lang2))

        logger.debug(f"Loaded {len(pairs)} language pairs")
        return pairs

    except FileNotFoundError as e:
        logger.error(f"Supporting languages file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading language pairs: {e}")
        raise


def count_languages(filepath: Optional[str] = None) -> Counter[str]:
    """
    Count the frequency of each language in the supporting languages file.

    Args:
        filepath: Optional path to the supporting languages file

    Returns:
        Counter with language frequencies
    """
    if filepath is None:
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "supporting_languages.txt"
        )

    logger.debug(f"Counting language frequencies in {filepath}")

    lang_counter: Counter[str] = Counter()

    try:
        with open(filepath, "r") as f:
            for line in f:
                pair = line.strip()
                if not pair or "-" not in pair:
                    continue

                parts = pair.split("-")
                if len(parts) == 2:
                    lang1, lang2 = parts
                    lang_counter[lang1] += 1
                    lang_counter[lang2] += 1

        logger.debug(f"Found {len(lang_counter)} unique languages")
        return Counter(dict(lang_counter.most_common()))

    except Exception as e:
        logger.error(f"Error counting languages: {e}")
        return Counter()


def main() -> None:
    """Main function for downloading word2word files."""
    logger.debug("Starting word2word file download process")

    try:
        # Load language pairs
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "supporting_languages.txt"
        )

        pairs = load_language_pairs(filepath)

        if not pairs:
            logger.error("No language pairs found to download")
            return

        # Filter for Estonian pairs only
        et_pairs = [(l1, l2) for l1, l2 in pairs if l1 == "et" or l2 == "et"]
        logger.debug(f"Found {len(et_pairs)} Estonian language pairs to download")

        # Download files using thread pool
        logger.debug("Starting parallel downloads")
        thread_map(
            download_pkl, et_pairs, max_workers=8, desc="Downloading translation files"
        )

        logger.debug("Download process completed")

    except Exception as e:
        logger.critical(f"Critical error in download process: {e}")
        raise


if __name__ == "__main__":
    # Uncomment to display language statistics
    # lang_counter = count_languages()
    # print("Language counts:")
    # for lang, count in lang_counter.items():
    #     print(f"{lang}: {count}")

    main()

    # with open("data/translations/downloads/fr-en.pkl", "rb") as f:
    #     word2x, y2word, x2ys = pickle.load(f)

    #     for fr_word, x in word2x.items():
    #         ys = x2ys.get(x, [])
    #         if ys:
    #             words = [y2word[y] for y in ys]
    #             print(f"{fr_word}: {', '.join(words)}")
    #             input()
