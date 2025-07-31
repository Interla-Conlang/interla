"""
This module assigns orthographic forms (spellings) to the Interla vocabulary
by computing similarity scores between Interla tokens and words from multiple
languages, then solving an optimal assignment problem.

Abbreviations:
- et: Estonian
- int: Interla
- anon: anonymous
- orth: orthographied
"""

import os
import pickle
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from assign_spellings_common import get_data_from_opensub
from logging_config import logger


def get_int_orth_tokens() -> List[str]:
    """
    Load all Interla orthographic tokens from the vocabulary file.

    Returns:
        List of Interla orthographic tokens

    Raises:
        FileNotFoundError: If pronounceable_combinations.csv is not found
    """
    logger.debug("Loading Interla orthographic tokens")

    try:
        interla_df = pd.read_csv("output/pronounceable_combinations.csv")
        int_orth_tokens = list(set(interla_df["word"].tolist()))

        logger.debug(f"Loaded {len(int_orth_tokens)} interla orthographic tokens")
        return int_orth_tokens

    except FileNotFoundError as e:
        logger.error(f"Could not find pronounceable combinations file: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load orthographic tokens: {e}")
        raise


def process_int_orth_token(args: Tuple[int, str]) -> List[Tuple[int, int, float]]:
    """
    Process a single Interla orthographic token to find best anonymous token matches.

    Args:
        args: Tuple of (index, int_orth_token) to process

    Returns:
        List of tuples (token_index, anon_token, average_distance)
    """
    i, int_orth_token = args
    results = []

    # Access global variables (available in multiprocessing context)
    global int_anon_tokens_coocurrences, all_y2normWord, LANG_WEIGHTS

    for int_anon_token, assoc_words in int_anon_tokens_coocurrences.items():
        distances = {}

        # Calculate distance to normalized words in each language
        for lang, word_id in assoc_words.items():
            y2normWord = all_y2normWord.get(lang, {})
            norm_w = y2normWord.get(word_id)

            if norm_w is not None:
                # Calculate similarity ratio with cutoff for efficiency
                distance = 1 - ratio(int_orth_token, norm_w, score_cutoff=50) / 100
                distances[lang] = distance

        # Calculate weighted average distance
        total_weight = sum(LANG_WEIGHTS[lang] for lang in distances)
        if total_weight > 0:
            avg_dist = (
                sum(distances[lang] * LANG_WEIGHTS[lang] for lang in distances)
                / total_weight
            )
            # Only include non-perfect matches (distance != 1.0)
            if avg_dist != 1.0:
                results.append((i, int_anon_token, avg_dist))

    return results


def step_2(int_orth_tokens: List[str]) -> List[List[Tuple[int, int, float]]]:
    """
    Calculate similarity scores between orthographic and anonymous tokens.

    This step computes the similarity between each Interla orthographic token
    and all anonymous tokens based on their associated words in various languages.

    Args:
        int_orth_tokens: List of Interla orthographic tokens

    Returns:
        List of results for each orthographic token
    """
    logger.debug("Starting step 2: calculating token similarities")

    results_pkl_path = "output/coocurrences.pkl"

    if os.path.exists(results_pkl_path):
        logger.debug("Loading cached similarity results")
        try:
            with open(results_pkl_path, "rb") as f:
                all_results = pickle.load(f)
            logger.debug(f"Loaded {len(all_results)} cached results")
        except Exception as e:
            logger.error(f"Failed to load cached results: {e}")
            raise
    else:
        logger.debug(f"Computing similarities for {len(int_orth_tokens)} tokens")
        logger.warning("This step may take ~20 minutes")

        try:
            all_results = process_map(
                process_int_orth_token,
                list(enumerate(int_orth_tokens)),
                max_workers=12,
                desc="Processing tokens",
            )

            logger.debug("Saving similarity results to cache")
            with open(results_pkl_path, "wb") as f:
                pickle.dump(all_results, f)

        # TODO: Flatten the list of results

        except Exception as e:
            logger.error(f"Failed to compute similarities: {e}")
            raise

    return all_results


def step_3(
    int_orth_tokens: List[str],
    int_anon_tokens_coocurrences: Dict[int, Dict[str, int]],
    all_results: List[List[Tuple[int, int, float]]],
) -> Dict[int, int]:
    """
    Solve the optimal assignment problem between orthographic and anonymous tokens.

    This step builds a bipartite graph and uses the Hungarian algorithm to find
    the minimum-cost perfect matching.

    Args:
        int_orth_tokens: List of orthographic tokens
        int_anon_tokens_coocurrences: Anonymous token cooccurrences
        all_results: Similarity computation results from step 2

    Returns:
        Dictionary mapping orthographic token indices to anonymous token indices
    """
    logger.debug("Starting step 3: solving optimal assignment")

    matching_pkl_path = "output/interla_matching.pkl"

    if os.path.exists(matching_pkl_path):
        logger.debug("Loading cached matching results")
        try:
            with open(matching_pkl_path, "rb") as f:
                matching = pickle.load(f)
            logger.debug(f"Loaded matching with {len(matching)} assignments")
        except Exception as e:
            logger.error(f"Failed to load cached matching: {e}")
            raise
    else:
        logger.debug("Computing optimal assignment")

        # Build biadjacency matrix
        biadjacency_dump_path = "output/biadjacency_matrix.npy"

        if os.path.exists(biadjacency_dump_path):
            logger.debug("Loading cached biadjacency matrix")
            biadjacency = np.load(biadjacency_dump_path)
        else:
            logger.debug("Building biadjacency matrix")
            nb_orth_tokens = len(int_orth_tokens)
            nb_anon_tokens = len(int_anon_tokens_coocurrences)

            logger.debug(f"Matrix dimensions: {nb_orth_tokens} x {nb_anon_tokens}")

            # Use a dense numpy array for insertion (default to 1.0 for maximum distance)
            biadjacency = np.ones((nb_orth_tokens, nb_anon_tokens), dtype=np.float16)

            logger.debug("Populating biadjacency matrix with similarity scores")
            for result_list in tqdm(all_results, desc="Building matrix"):
                for int_orth_token_idx, int_anon_token, avg_dist in result_list:
                    biadjacency[int_orth_token_idx, int_anon_token] = avg_dist

            # Save the biadjacency matrix for debugging
            logger.debug(f"Saving biadjacency matrix to {biadjacency_dump_path}")
            np.save(biadjacency_dump_path, biadjacency)

        logger.debug("Solving assignment problem using Hungarian algorithm")
        try:
            # Compute the minimum weight full matching using linear_sum_assignment
            row_ind, col_ind = linear_sum_assignment(biadjacency, maximize=False)

            # Build matching dict: int_orth_token_idx -> int_anon_token_idx
            matching = {i.item(): j.item() for i, j in zip(row_ind, col_ind)}

            logger.debug(f"Found optimal matching with {len(matching)} assignments")

            # Save the matching to a file
            logger.debug(f"Saving matching results to {matching_pkl_path}")
            with open(matching_pkl_path, "wb") as f:
                pickle.dump(matching, f)

        except Exception as e:
            logger.error(f"Failed to solve assignment problem: {e}")
            raise

    return matching


def display_results(
    int_orth_tokens: List[str],
    matching: Dict[int, int],
    int_anon_tokens_coocurrences: Dict[int, Dict[str, int]],
    all_y2word: Dict[str, Dict[int, str]],
) -> None:
    """
    Display the final matching results.

    Args:
        int_orth_tokens: List of orthographic tokens
        matching: Optimal assignment mapping
        int_anon_tokens_coocurrences: Anonymous token cooccurrences
        all_y2word: Mapping from language to word IDs to words
    """
    logger.debug("Displaying matching results")

    displayed_count = 0
    missing_count = 0

    for i, int_orth_token in enumerate(int_orth_tokens):
        if i in matching:
            j = matching[i]
            assoc_words = int_anon_tokens_coocurrences.get(j, {})

            print(f"Interla: {int_orth_token}")
            for lang, y_id in assoc_words.items():
                y2word = all_y2word.get(lang, {})
                word = y2word.get(y_id, "")
                print(f"  {lang}: {word}")
            print()

            displayed_count += 1
        else:
            missing_count += 1
            logger.debug(f"Token index {i} not found in matching")

    logger.debug(f"Displayed {displayed_count} matched tokens")
    if missing_count > 0:
        logger.warning(f"{missing_count} tokens were not matched")


def main() -> None:
    """Main function for spelling assignment to vocabulary."""
    logger.debug("Starting spelling assignment to vocabulary")

    try:
        # Step 1: Load orthographic tokens
        logger.debug("Step 1: Loading orthographic tokens")
        int_orth_tokens = get_int_orth_tokens()

        # Load anonymous tokens and associated data
        logger.debug("Loading anonymous tokens and language data")
        N = 7_000  # Limit number of tokens for processing
        logger.debug(f"Processing top {N} tokens")

        global int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS
        int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = (
            get_data_from_opensub(N)
        )

        # Step 2: Calculate similarities
        all_results = step_2(int_orth_tokens)

        # Step 3: Solve optimal assignment
        matching = step_3(int_orth_tokens, int_anon_tokens_coocurrences, all_results)

        # Display results
        display_results(
            int_orth_tokens, matching, int_anon_tokens_coocurrences, all_y2word
        )

        logger.debug("Spelling assignment to vocabulary completed successfully")

    except Exception as e:
        logger.critical(f"Critical error in spelling assignment: {e}")
        raise


if __name__ == "__main__":
    main()
