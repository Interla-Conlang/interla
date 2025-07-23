"""
Alphabet selection module for the Interla project.

This module selects the optimal subset of IPA characters and their corresponding
letters based on their availability and usage across different languages.

The selection strategy:
- Avoid phonemes that are not used in many languages
- Prefer characters that are pronounced similarly in many languages
- Maximize the character set size to allow for a rich vocabulary
- Maintain bijection between IPA characters and letters
"""

import os
from collections import Counter
from typing import Dict, Tuple

import pandas as pd

from logging_config import logger
from utils import get_lang_weights


def load_phoneme_data(languages: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Load phoneme data for all available languages.

    Args:
        languages: DataFrame containing language information

    Returns:
        Dictionary mapping language names to their phoneme DataFrames
    """
    logger.debug("Loading phoneme data from phonems.ods")
    phonems_sheets = {}

    for lang in languages["Language"]:
        try:
            phonems = pd.read_excel("data/phonems.ods", sheet_name=lang)
            phonems_sheets[lang] = phonems
            logger.debug(f"Loaded phoneme data for {lang}: {len(phonems)} entries")
        except ValueError:
            logger.warning(f"Sheet for language '{lang}' not found in phonems.ods")
        except Exception as e:
            logger.error(f"Failed to load phoneme data for {lang}: {e}")

    logger.debug(
        f"Successfully loaded phoneme data for {len(phonems_sheets)} languages"
    )
    return phonems_sheets


def compute_ipa_letter_pairs(
    phonems_sheets: Dict[str, pd.DataFrame], weights: Dict[str, float]
) -> Counter[Tuple[str, str]]:
    """
    Compute weighted frequency of IPA-letter pairs across languages.

    Args:
        phonems_sheets: Dictionary of language phoneme data
        weights: Language weights for computing frequencies

    Returns:
        Counter with IPA-letter pairs and their weighted frequencies
    """
    logger.debug("Computing optimal IPA-letter pairs")
    pair_counter: Counter[Tuple[str, str]] = Counter()

    processed_languages = 0
    total_pairs = 0

    for lang, df in phonems_sheets.items():
        if lang not in weights:
            logger.warning(f"No weight found for language {lang}, skipping")
            continue

        lang_pairs = 0
        weight = weights[lang]

        for _, row in df.iterrows():
            # Parse IPA and letter values (can be comma-separated)
            ipa_vals = str(row["IPA"]).split(",") if pd.notna(row["IPA"]) else []
            letter_vals = (
                str(row["letter"]).split(",") if pd.notna(row["letter"]) else []
            )

            # Clean up values
            ipa_vals = [v.strip() for v in ipa_vals if v.strip() and v.strip() != "nan"]
            letter_vals = [
                v.strip() for v in letter_vals if v.strip() and v.strip() != "nan"
            ]

            # Create all combinations of IPA-letter pairs
            for ipa in ipa_vals:
                for letter in letter_vals:
                    pair = (ipa, letter)
                    pair_counter[pair] += weight  # type: ignore
                    lang_pairs += 1
                    total_pairs += 1

        logger.debug(f"Processed {lang_pairs} pairs for {lang} (weight: {weight:.3f})")
        processed_languages += 1

    logger.debug(
        f"Processed {processed_languages} languages, {total_pairs} total weighted pairs"
    )
    logger.debug(f"Found {len(pair_counter)} unique IPA-letter pairs")

    return pair_counter


def create_alphabet_dataframe(pair_counter: Counter[Tuple[str, str]]) -> pd.DataFrame:
    """
    Create a sorted DataFrame of IPA-letter pairs with weights.

    Args:
        pair_counter: Counter of IPA-letter pairs with frequencies

    Returns:
        DataFrame with IPA, Letter, and Weight columns sorted by weight
    """
    logger.debug("Creating sorted alphabet DataFrame")

    # Sort pairs by frequency (descending)
    sorted_pairs = sorted(pair_counter.items(), key=lambda x: x[1], reverse=True)
    logger.debug(f"Sorted {len(sorted_pairs)} pairs by weight")

    # Create DataFrame
    sorted_df = pd.DataFrame(
        [(ipa, letter, weight) for (ipa, letter), weight in sorted_pairs],
        columns=["IPA", "Letter", "Weight"],
    )

    logger.debug(f"Created DataFrame with {len(sorted_df)} IPA-letter pairs")
    return sorted_df


def enforce_bijection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce bijection constraint: each IPA and letter can only appear once.

    Args:
        df: DataFrame with IPA-letter pairs sorted by weight

    Returns:
        Filtered DataFrame maintaining bijection constraint
    """
    logger.debug("Enforcing bijection constraint (one-to-one mapping)")

    used_letters = set()
    used_ipas = set()
    indices_to_drop = []

    for idx, row in df.iterrows():
        letter = row["Letter"]
        ipa = row["IPA"]

        if letter not in used_letters and ipa not in used_ipas:
            used_letters.add(letter)
            used_ipas.add(ipa)
            logger.debug(
                f"Accepted pair: {ipa} -> {letter} (weight: {row['Weight']:.3f})"
            )
        else:
            # Mark for removal if either letter or IPA is already used
            indices_to_drop.append(idx)
            reason = []
            if letter in used_letters:
                reason.append(f"letter '{letter}' already used")
            if ipa in used_ipas:
                reason.append(f"IPA '{ipa}' already used")
            logger.debug(f"Rejected pair: {ipa} -> {letter} ({', '.join(reason)})")

    # Drop rejected pairs
    filtered_df = df.drop(indices_to_drop)

    logger.debug(
        f"Bijection enforcement: kept {len(filtered_df)} pairs, dropped {len(indices_to_drop)}"
    )
    return filtered_df


def apply_weight_threshold(df: pd.DataFrame, threshold: float = 0.2) -> pd.DataFrame:
    """
    Filter pairs by minimum weight threshold.

    Args:
        df: DataFrame with IPA-letter pairs
        threshold: Minimum weight threshold

    Returns:
        Filtered DataFrame with pairs above threshold
    """
    logger.debug(f"Applying weight threshold: {threshold}")

    original_count = len(df)
    filtered_df = df[df["Weight"] > threshold].copy()
    filtered_count = len(filtered_df)

    logger.debug(
        f"Weight filtering: kept {filtered_count} pairs, dropped {original_count - filtered_count}"
    )

    if filtered_count == 0:
        logger.warning(f"No pairs meet the weight threshold of {threshold}")

    return filtered_df


def save_alphabet(df: pd.DataFrame, output_file: str = "output/alphabet.csv") -> None:
    """
    Save the alphabet DataFrame to a CSV file.

    Args:
        df: DataFrame containing the selected alphabet
        output_file: Output file path

    Raises:
        PermissionError: If cannot write to output file
    """
    logger.debug(f"Saving alphabet to {output_file}")

    try:
        os.makedirs("output", exist_ok=True)
        df.to_csv(output_file, index=False)
        logger.debug(f"Successfully saved {len(df)} alphabet entries to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save alphabet to {output_file}: {e}")
        raise


def main() -> None:
    """Main function for alphabet selection."""
    logger.debug("Starting alphabet selection process")

    try:
        # Load language weights
        logger.debug("Loading language weights")
        languages, weights = get_lang_weights()
        logger.debug(f"Loaded weights for {len(weights)} languages")

        # Load phoneme data
        phonems_sheets = load_phoneme_data(languages)

        if not phonems_sheets:
            logger.error("No phoneme data loaded, cannot proceed")
            raise ValueError("No phoneme data available")

        # Compute IPA-letter pair frequencies
        pair_counter = compute_ipa_letter_pairs(phonems_sheets, weights)

        # Create sorted DataFrame
        sorted_df = create_alphabet_dataframe(pair_counter)

        # Enforce bijection constraint
        bijection_df = enforce_bijection(sorted_df)

        # Apply weight threshold
        # TODO: find a better criteria to choose how much characters we want in interla
        final_df = apply_weight_threshold(bijection_df, threshold=0.2)

        # Save results
        save_alphabet(final_df)

        # Display results
        logger.debug("Final alphabet selection:")
        print("Selected Alphabet:")
        print(final_df.to_string(index=False))

        logger.debug(
            f"Alphabet selection complete: {len(final_df)} characters selected"
        )

        # TODO: Consider implementing confusion matrix to avoid sounds that are
        # often mistaken for each other in some languages

    except Exception as e:
        logger.critical(f"Critical error in alphabet selection: {e}")
        raise


if __name__ == "__main__":
    main()
