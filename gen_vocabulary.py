"""
Vocabulary generation module for the Interla project.

This module generates all possible pronounceable combinations of letters
from the Interla alphabet, applying phonetic rules to filter out
unpronounceable sequences.
"""

import itertools
from typing import Dict, List, Set

import pandas as pd
from tqdm import tqdm

from logging_config import logger


def load_alphabet() -> Dict[str, str]:
    """
    Load the Interla alphabet from the CSV file.

    Returns:
        Dictionary mapping letters to their phonetic representations
    """
    logger.debug("Loading alphabet from output/alphabet.csv")
    try:
        df = pd.read_csv("output/alphabet.csv")
        alphabet = df.set_index("Letter")["IPA"].to_dict()
        logger.debug(f"Loaded {len(alphabet)} letters from alphabet: {alphabet}")
        return alphabet
    except FileNotFoundError as e:
        logger.error(f"Could not find alphabet CSV file: {e}")
        return {}


alphabet = load_alphabet()
LETTERS = list(alphabet.keys())
IPA_LETTERS = list(alphabet.values())
VOWELS = set("aeiou")
CONSONANTS = set(LETTERS) - VOWELS
IPA_VOWELS = set(IPA_LETTERS) & set("aeiou")  # Define your IPA vowels here
IPA_CONSONANTS = set(IPA_LETTERS) - IPA_VOWELS


def generate_letter_combinations(letters: List[str], max_length: int = 5) -> Set[str]:
    """
    Generate all possible combinations of letters with underscores.

    This function creates combinations where:
    - Single letters can be with or without underscores
    - Multi-letter combinations have first letter optionally with underscore,
      and following letters always with underscores

    Args:
        letters: List of letters to combine
        max_length: Maximum length of combinations to generate

    Returns:
        Set of all possible letter combinations
    """
    logger.debug(f"Generating letter combinations up to length {max_length}")

    letters_with_underscore = [f"_{letter}" for letter in letters]
    logger.debug(f"Created {len(letters_with_underscore)} underscore variants")

    combinations: Set[str] = set()

    for r in tqdm(range(1, max_length + 1), desc="Generating combinations"):
        if r == 1:
            # Only one letter, can be from letters or letters_with_underscore
            combinations.update(letters)
            combinations.update(letters_with_underscore)
            logger.debug(
                f"Added {len(letters) + len(letters_with_underscore)} single-letter combinations"
            )
        else:
            # First letter: from letters or letters_with_underscore
            # Following letters: always from letters_with_underscore
            for first in letters + letters_with_underscore:
                for rest in itertools.product(letters_with_underscore, repeat=r - 1):
                    combinations.add(first + "".join(rest))

            logger.debug(f"Generated combinations of length {r}")

    logger.debug(f"Generated {len(combinations)} total combinations")
    return combinations


def is_pronounceable(combo: str) -> bool:
    """
    Check if a letter combination is pronounceable according to phonetic rules.

    Rules applied:
    - No more than 2 consecutive vowels
    - No more than 1 consecutive consonant
    - No two consecutive identical vowels

    Args:
        combo: Letter combination to check

    Returns:
        True if the combination is pronounceable, False otherwise
    """
    # Split the combo at underscores
    parts = combo.split("_")
    # Remove empty strings from split (in case combo starts with "_")
    parts = [p for p in parts if p]

    vowel_count = 0
    consonant_count = 0
    prev_vowel = None

    for p in parts:
        if p in VOWELS:
            # Forbid two consecutive same vowels
            if prev_vowel == p:
                return False
            vowel_count += 1
            consonant_count = 0
            prev_vowel = p
        elif p in CONSONANTS:
            consonant_count += 1
            vowel_count = 0
            prev_vowel = None
        else:
            # Unknown character, reset counters
            vowel_count = 0
            consonant_count = 0
            prev_vowel = None

        # Check phonetic constraints
        if vowel_count > 2 or consonant_count > 1:
            return False

    return True


def path_pronounciability_weight(path: List[str], path_weights: List[float]) -> float:
    """
    Calculate the total pronounciability weight for a path of characters.

    Weight calculation is based on phonetic rules:
    - Base weight of 1.0 per character
    - +inf penalty for more than 2 consecutive vowels
    - +inf penalty for more than 1 consecutive consonant
    - +inf penalty for two consecutive identical vowels
    - Ignores "-" tokens when checking consecutivity

    Args:
        path: List of characters representing the path
        path_weights: List of weights corresponding to each character in the path

    Returns:
        Total pronounciability weight for the path (lower is better)
    """
    if not path:
        return 0.0

    # Filter out "-" tokens for consecutivity checks
    filtered_path = [char for char in path if char != "-"]

    if not filtered_path:
        return 0.0

    total_weight = sum(path_weights)  # Start with negative sum of weights

    vowel_count = 0
    consonant_count = 0
    prev_vowel = None

    for char in filtered_path:
        if char in IPA_VOWELS:
            # Check for consecutive identical vowels (forbidden)
            if prev_vowel == char:
                return float("inf")

            vowel_count += 1
            consonant_count = 0
            prev_vowel = char

        elif char in IPA_CONSONANTS:
            consonant_count += 1
            vowel_count = 0
            prev_vowel = None

        else:
            # Unknown character, reset counters
            vowel_count = 0
            consonant_count = 0
            prev_vowel = None

        # Apply penalties for violating phonetic constraints
        if vowel_count > 2:
            return float("inf")
        if consonant_count > 1:
            return float("inf")

    return total_weight


def filter_pronounceable_combinations(combinations: Set[str]) -> List[str]:
    """
    Filter combinations to keep only pronounceable ones.

    Args:
        combinations: Set of all generated combinations

    Returns:
        List of pronounceable combinations
    """
    logger.debug(f"Filtering {len(combinations)} combinations for pronounceability")

    # Define vowels and consonants
    logger.debug(f"Vowels: {VOWELS}")
    logger.debug(f"Consonants: {CONSONANTS}")

    pronounceable = []
    filtered_count = 0

    for combo in tqdm(combinations, desc="Filtering combinations"):
        if is_pronounceable(combo):
            pronounceable.append(combo)
        else:
            filtered_count += 1

    logger.debug(f"Kept {len(pronounceable)} pronounceable combinations")
    logger.debug(f"Filtered out {filtered_count} unpronounceable combinations")

    return pronounceable


def save_combinations(combinations: List[str], filename: str) -> None:
    """
    Save pronounceable combinations to a CSV file.

    Args:
        combinations: List of pronounceable combinations
        filename: Output filename for CSV

    Raises:
        PermissionError: If cannot write to output file
    """
    logger.debug(f"Saving {len(combinations)} combinations to {filename}")

    try:
        df = pd.DataFrame({"word": combinations})
        df.to_csv(filename, index=False)
        logger.debug(f"Successfully saved combinations to {filename}")
    except Exception as e:
        logger.error(f"Failed to save combinations to {filename}: {e}")
        raise


def main() -> None:
    """Main function for vocabulary generation."""
    logger.debug("Starting vocabulary generation")

    try:
        # Generate all combinations
        logger.debug("Generating letter combinations")
        combinations = generate_letter_combinations(LETTERS, max_length=5)

        # Filter for pronounceable combinations
        logger.debug("Filtering for pronounceable combinations")
        pronounceable = filter_pronounceable_combinations(combinations)

        # Save results
        output_file = "output/pronounceable_combinations.csv"
        save_combinations(pronounceable, output_file)

        logger.debug(
            f"Vocabulary generation complete: {len(pronounceable)} words generated"
        )
        print(f"Total pronounceable combinations: {len(pronounceable)}")

        # TODO: how to avoid confusing for example "a bao" and "abao"
        # => Huffman tree? or stress on the first syllable will handle this confusion?

    except Exception as e:
        logger.critical(f"Critical error in vocabulary generation: {e}")
        raise


# TODO: how to filter out combinations that are impossible to pronounce???
# TODO: i think the best way is empirically to find the combinations thta are present in the languages

if __name__ == "__main__":
    main()
