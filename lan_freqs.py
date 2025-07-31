import os
from typing import Dict

import pandas as pd

DATA_DIR = "data/frequencies/downloads"


def get_freq_dicts() -> Dict[str, Dict[str, float]]:
    """
    Load frequency dictionaries from text files in the specified directory.

    Returns:
        Dictionary mapping language codes to their frequency dictionaries
    """

    FREQ_DICT = {}

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            lang = filename.split(".")[0]
            filepath = os.path.join(DATA_DIR, filename)
            df = pd.read_csv(filepath, sep=" ", header=None, names=["word", "count"])
            total_count = df["count"].sum()
            freq_dict = dict(zip(df["word"], df["count"] / total_count))
            FREQ_DICT[lang] = freq_dict

    return FREQ_DICT


FREQ_DICT = get_freq_dicts()
