import numpy as np
import pandas as pd

L2_WEIGHT = 0.5  # Weight for L2 speakers in the total weight calculation


# Extracting data
def get_lang_weights():
    languages = pd.read_excel("data/languages.ods")

    total_l1_speakers = languages["L1_speakers"].sum()
    total_l2_speakers = languages["L2_speakers"].sum()
    total_weight = total_l1_speakers + total_l2_speakers * L2_WEIGHT

    languages["weight"] = (
        languages["L1_speakers"] + languages["L2_speakers"] * L2_WEIGHT
    )
    languages["weight"] /= total_weight  # Normalize weights
    weights = {
        lang: weight for lang, weight in zip(languages["Language"], languages["weight"])
    }

    assert np.isclose(languages["weight"].sum(), 1.0), "Weights should sum to 1"

    return languages, weights
