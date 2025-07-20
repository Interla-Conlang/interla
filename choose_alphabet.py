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

import pandas as pd

from utils import get_lang_weights

if __name__ == "__main__":
    languages, weights = get_lang_weights()
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

    # TODO: i think we should also use "confusion matrix" to avoid sounds that are often mistaken for each other in some languages

    # Sort pairs by frequency
    sorted_pairs = sorted(pair_counter.items(), key=lambda x: x[1], reverse=True)
    # Create a DataFrame with separate columns for IPA and letter
    sorted_df = pd.DataFrame(
        [(ipa, letter, weight) for (ipa, letter), weight in sorted_pairs],
        columns=["IPA", "Letter", "Weight"],
    )

    # BIJECTION assumption: as soon as a letter or a IPA character is used, should no appear a in the df
    used_letters = set()
    used_ipas = set()
    for _, row in sorted_df.iterrows():
        if row["Letter"] not in used_letters and row["IPA"] not in used_ipas:
            used_letters.add(row["Letter"])
            used_ipas.add(row["IPA"])
        else:
            # If either the letter or the IPA is already used, we skip this pair
            sorted_df.drop(index=row.name, inplace=True)

    # TODO: find a better criteria to choose how much characters we want in interla
    sorted_df = sorted_df[sorted_df["Weight"] > 0.2]

    # Save the sorted DataFrame to `alphabet.csv`
    os.makedirs("output", exist_ok=True)
    sorted_df.to_csv("output/alphabet.csv", index=False)

    print(sorted_df)
