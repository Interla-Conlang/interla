"""
Abbreviations:
- et: Estonian
- int: Interla
- anon: anonymous
- orth: orthographied
"""

import os
import pickle

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from assign_spellings_common import step_1


# 2. Load all interla tokens
def get_int_orth_tokens():
    interla_df = pd.read_csv("output/pronounceable_combinations.csv")
    int_orth_tokens = list(set(interla_df["word"].tolist()))

    print(len(int_orth_tokens), "interla orthographied tokens")
    return int_orth_tokens


int_orth_tokens = get_int_orth_tokens()

# 3. Collect all "et" words and their associated words from all other languages
N = 7_000
int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1(N)


# FIXME: ~ 20mn long
def process_int_orth_token(args):
    i, int_orth_token = args
    results = []
    for int_anon_token, assoc_words in int_anon_tokens_coocurrences.items():
        distances = dict()

        # for lang, ids in assoc_words.items():
        #     dists = []
        #     y2word = all_y2word.get(lang, {})
        #     for y_id in ids:
        #         w = y2word.get(y_id)
        #         if w is not None:
        #             distance = 1 - ratio(int_orth_token, w) / 100
        #             dists.append(distance)
        #     if dists:
        #         avg_dist = sum(dists) / len(dists)
        #         distances[lang] = avg_dist

        for lang, id in assoc_words.items():
            y2normWord = all_y2normWord.get(lang, {})
            norm_w = y2normWord.get(id)
            if norm_w is not None:
                distance = 1 - ratio(int_orth_token, norm_w, score_cutoff=50) / 100
                distances[lang] = distance

        total_weight = sum(LANG_WEIGHTS[lang] for lang in distances)
        if total_weight > 0:
            avg_dist = (
                sum(distances[lang] * LANG_WEIGHTS[lang] for lang in distances)
                / total_weight
            )
            if avg_dist != 1.0:
                results.append((i, int_anon_token, avg_dist))
    return results


# Run in threads and collect all results
def step_2():
    results_pkl_path = "output/coocurrences.pkl"
    if os.path.exists(results_pkl_path):
        with open(results_pkl_path, "rb") as f:
            all_results = pickle.load(f)
    else:
        all_results = process_map(
            process_int_orth_token, list(enumerate(int_orth_tokens)), max_workers=12
        )
        with open(results_pkl_path, "wb") as f:
            pickle.dump(all_results, f)

    # TODO: Flatten the list of results
    return all_results


all_results = step_2()


def step_3():
    matching_pkl_path = "output/interla_matching.pkl"
    if os.path.exists(matching_pkl_path):
        with open(matching_pkl_path, "rb") as f:
            matching = pickle.load(f)
    else:
        # Build biadjacency matrix
        biadjacency_dump_path = "output/biadjacency_matrix.npy"

        if os.path.exists(biadjacency_dump_path):
            biadjacency = np.load(biadjacency_dump_path)
        else:
            nb_orth_tokens = len(int_orth_tokens)
            nb_anon_tokens = len(int_anon_tokens_coocurrences)

            # Use a dense numpy array for insertion
            biadjacency = np.ones(
                (nb_orth_tokens, nb_anon_tokens), dtype=np.float16
            )  # default to 1.0

            for result_list in tqdm(all_results):
                for int_orth_token, int_anon_token, avg_dist in result_list:
                    biadjacency[int_orth_token, int_anon_token] = avg_dist

            # Dump the biadjacency matrix for debugging
            np.save(biadjacency_dump_path, biadjacency)

        # Compute the minimum weight full matching using linear_sum_assignment
        row_ind, col_ind = linear_sum_assignment(biadjacency, maximize=False)

        # Build matching dict: int_orth_token -> int_anon_token
        matching = {i.item(): j.item() for i, j in zip(row_ind, col_ind)}

        # Save the matching to a file
        with open(matching_pkl_path, "wb") as f:
            pickle.dump(matching, f)

    return matching


matching = step_3()

# Then display the words from A with all their associated "w = y2word.get(y_id)"
for i, int_orth_token in enumerate(int_orth_tokens):
    if i in matching:  # TODO: why some idx don't exist in matching?
        j = matching[i]
        assoc_words = int_anon_tokens_coocurrences.get(j, {})
        print(f"Interla: {int_orth_token}")
        for lang, y_id in assoc_words.items():
            y2word = all_y2word.get(lang, {})
            word = y2word.get(y_id, "")
            print(f"  {lang}: {word}")
        print()
