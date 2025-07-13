import itertools

import pandas as pd

# Load the alphabet CSV
df = pd.read_csv("output/alphabet.csv")

# Get the list of letters
letters = df["Letter"].tolist()
letters_with_underscore = [
    f"_{letter}" for letter in letters
]  # Add underscores to each letter

# Generate all combinations of 1, 2, or 3 letters, first letter without underscore, other letters with underscore
combinations = set()
for r in range(1, 4):
    if r == 1:
        # Only one letter, can be from letters or letters_with_underscore
        combinations.update(letters)
        combinations.update(letters_with_underscore)
    else:
        # First letter: from letters or letters_with_underscore
        for first in letters + letters_with_underscore:
            # Following letters: always from letters_with_underscore
            for rest in itertools.product(letters_with_underscore, repeat=r - 1):
                combinations.add(first + "".join(rest))

# TODO: how to filter out combinations that are impossible to pronounce???
# TODO: i think the best way is empirically to find the combinations thta are present in the languages
# For now, we do this very naively, by forbidding more than 2 consecutive vowels or 1 consonants
vowels = set("aeiou")
consonants = set(letters) - vowels  # All letters that are not vowels


def is_pronounceable(combo):
    # Split the combo at underscores
    parts = combo.split("_")
    # Remove empty strings from split (in case combo starts with "_")
    parts = [p for p in parts if p]
    # Check for more than 2 consecutive vowels or consonants in the splits
    vowel_count = 0
    consonant_count = 0
    for p in parts:
        if p in vowels:
            vowel_count += 1
            consonant_count = 0
        elif p in consonants:
            consonant_count += 1
            vowel_count = 0
        else:
            vowel_count = 0
            consonant_count = 0
        if vowel_count > 2 or consonant_count > 1:
            return False
    return True


# Filter combinations to keep only pronounceable ones
combinations = [combo for combo in combinations if is_pronounceable(combo)]

# TODO: how to avoid confusing for example "a bao" and "abao" => Huffman tree? or stress on the first syllable will handle this confusion?

# Example: print or save the combinations
for combo in combinations:
    print(combo)
print("Total combinations:", len(combinations))
