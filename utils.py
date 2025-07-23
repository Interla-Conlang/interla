import glob
import os
from typing import Dict

import numpy as np
import pandas as pd

L2_WEIGHT = 0.5  # Weight for L2 speakers in the total weight calculation

interla_alphabet = pd.read_csv("output/alphabet.csv")
VALID_INT_IPA = set(interla_alphabet["IPA"])
IPA_TO_INTERLA = dict(zip(interla_alphabet["IPA"], interla_alphabet["Letter"]))
INTERLA_TO_IPA = dict(zip(interla_alphabet["Letter"], interla_alphabet["IPA"]))

# All valid languages
pkl_dir = "data/translations/downloads"
pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
ALL_VALID_LANGUAGES = [
    os.path.basename(f).split("-")[1].split(".")[0]
    for f in pkl_files
    if os.path.basename(f).startswith("et-")
]


# Extracting data
def get_lang_weights():
    languages = pd.read_csv("data/languages.csv")

    # Reconstruct L1 and L2 speakers
    languages["L1_speakers"] = languages["Native Speakers"]
    languages["L2_speakers"] = (
        languages["Total Speakers"] - languages["Native Speakers"]
    )

    languages["weight"] = (
        languages["L1_speakers"] + languages["L2_speakers"] * L2_WEIGHT
    )

    # Group by Language_code and sum the weights
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

    # [TEMPORARY FIX] Missing languages have weight = to the minimal current weight
    min_weight = min(weights.values())
    for lang in ALL_VALID_LANGUAGES:
        if lang not in weights:
            weights[lang] = min_weight

    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        for lang in weights:
            weights[lang] /= total_weight

    assert np.isclose(sum(weights.values()), 1.0), "Weights should sum to 1"

    return languages, weights


if __name__ == "__main__":
    languages, weights = get_lang_weights()
    print("Languages and their weights:")
    print(languages[["Language", "weight"]])
    print("\nWeights dictionary:")
    print(weights)
