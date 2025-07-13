"""
We should choose the subset of characters based on their availability in the different existing languages of the world, and choose
the pronunciation of the characters based on the most common languages.

Intuitively:
- we should avoid phonems that are not used in many languages
- we should prefer characters that are pronounced similarly in many languages
- we should have as many characters as possible, to allow for a rich set of words
"""

import os
from collections import Counter

import numpy as np
import pandas as pd

L2_WEIGHT = 0.5  # Weight for L2 speakers in the total weight calculation

# Extracting data
languages = pd.read_excel("data/languages.ods")

total_l1_speakers = languages["L1_speakers"].sum()
total_l2_speakers = languages["L2_speakers"].sum()
total_weight = total_l1_speakers + total_l2_speakers * L2_WEIGHT

languages["weight"] = languages["L1_speakers"] + languages["L2_speakers"] * L2_WEIGHT
languages["weight"] /= total_weight  # Normalize weights
weights = {
    lang: weight for lang, weight in zip(languages["Language"], languages["weight"])
}

assert np.isclose(languages["weight"].sum(), 1.0), "Weights should sum to 1"

phonems_sheets = {}
for lang in languages["Language"]:
    try:
        phonems = pd.read_excel("data/phonems.ods", sheet_name=lang)
        phonems_sheets[lang] = phonems
    except ValueError:
        print(f"Sheet for language '{lang}' not found in phonems.ods")

# Computing optimal pairs of IPA and letters
pair_counter = Counter()

for lang, df in phonems_sheets.items():
    for _, row in df.iterrows():
        ipa_vals = str(row["IPA"]).split(",")
        letter_vals = str(row["letter"]).split(",")
        ipa_vals = [v.strip() for v in ipa_vals if v.strip()]
        letter_vals = [v.strip() for v in letter_vals if v.strip()]
        for ipa in ipa_vals:
            for letter in letter_vals:
                pair = (ipa, letter)
                pair_counter[pair] += weights[lang]

# Sort pairs by frequency
sorted_pairs = sorted(pair_counter.items(), key=lambda x: x[1], reverse=True)
# Create a DataFrame with separate columns for IPA and letter
sorted_df = pd.DataFrame(
    [(ipa, letter, freq) for (ipa, letter), freq in sorted_pairs],
    columns=["IPA", "Letter", "Frequency"],
)
# Save the sorted DataFrame to `alphabet.csv`
os.makedirs("output", exist_ok=True)
sorted_df.to_csv("output/alphabet.csv", index=False)

print(sorted_df)
