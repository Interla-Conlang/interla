"""
Utility functions
"""

import glob
import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from logging_config import logger

L2_WEIGHT: float = 0.5  # Weight for L2 speakers in the total weight calculation

logger.debug("Loading interla alphabet from output/alphabet.csv")
interla_alphabet = pd.read_csv("output/alphabet.csv")
VALID_INT_IPA = set(interla_alphabet["IPA"])
IPA_TO_INTERLA = dict(zip(interla_alphabet["IPA"], interla_alphabet["Letter"]))
INTERLA_TO_IPA = dict(zip(interla_alphabet["Letter"], interla_alphabet["IPA"]))

# All valid languages
pkl_dir = "data/translations/downloads"
logger.debug(f"Scanning for .pkl files in {pkl_dir}")
pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
ALL_VALID_LANGUAGES = [
    os.path.basename(f).split("-")[1].split(".")[0]
    for f in pkl_files
    if os.path.basename(f).startswith("et-")
]
logger.debug(
    f"Found {len(ALL_VALID_LANGUAGES)} valid languages: {sorted(ALL_VALID_LANGUAGES)}"
)


# Extracting data
def get_lang_weights() -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Calculate language weights based on native and total speakers.

    Returns:
        Tuple containing:
            - DataFrame with language information and calculated weights
            - Dictionary mapping language codes to normalized weights

    Raises:
        FileNotFoundError: If data/languages.csv is not found
        AssertionError: If weights don't sum to approximately 1.0
    """
    logger.debug("Loading language data from data/languages.csv")
    try:
        languages = pd.read_csv("data/languages.csv")
    except FileNotFoundError as e:
        logger.error(f"Could not find languages.csv file: {e}")
        raise

    logger.debug("Calculating L1 and L2 speakers")
    # Reconstruct L1 and L2 speakers
    languages["L1_speakers"] = languages["Native Speakers"]
    languages["L2_speakers"] = (
        languages["Total Speakers"] - languages["Native Speakers"]
    )

    languages["weight"] = (
        languages["L1_speakers"] + languages["L2_speakers"] * L2_WEIGHT
    )
    logger.debug(f"Applied L2_WEIGHT of {L2_WEIGHT} to L2 speakers")

    # Group by Language_code and sum the weights
    logger.debug("Grouping languages by language code and summing weights")
    languages = (
        languages.groupby("Language_code")
        .agg(
            {
                "Language": "first",
                "weight": "sum",
                "L1_speakers": "sum",
                "L2_speakers": "sum",
            }
        )
        .reset_index()
    )

    weights: Dict[str, float] = {
        lang: weight
        for lang, weight in zip(languages["Language_code"], languages["weight"])
    }
    logger.debug(f"Created initial weights for {len(weights)} languages")

    # [TEMPORARY FIX] Missing languages have weight = to the minimal current weight
    min_weight = min(weights.values())
    logger.debug(f"Minimum weight found: {min_weight}")

    missing_langs = []
    for lang in ALL_VALID_LANGUAGES:
        if lang not in weights:
            weights[lang] = min_weight
            missing_langs.append(lang)

    if missing_langs:
        logger.warning(
            f"Added minimum weight for {len(missing_langs)} missing languages: {missing_langs}"
        )

    # Normalize weights
    total_weight = sum(weights.values())
    logger.debug(f"Total weight before normalization: {total_weight}")

    if total_weight > 0:
        for lang in weights:
            weights[lang] /= total_weight
        logger.debug("Normalized all language weights")
    else:
        logger.error("Total weight is zero, cannot normalize weights")
        raise ValueError("Total weight is zero")

    weight_sum = sum(weights.values())
    if not np.isclose(weight_sum, 1.0):
        logger.error(f"Weights sum to {weight_sum}, expected ~1.0")
        raise AssertionError("Weights should sum to 1")

    logger.debug(f"Successfully calculated weights for {len(weights)} languages")
    return languages, weights


_, LANG_WEIGHTS = get_lang_weights()
