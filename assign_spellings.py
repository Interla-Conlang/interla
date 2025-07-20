"""
Abbreviations:
- et: Estonian
- int: Interla
- anon: anonymous
- orth: orthographied
"""

import glob
import os
import pickle
import unicodedata
from collections import defaultdict

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from utils import get_lang_weights

N = 7_000
TO_KEEP = {
    "en",
    "zh_cn",
    # "hi",  # TODO: need transliteration
    "es",
    # "ar",  # TODO: need transliteration
    # "bn",  # TODO: need transliteration
    "fr",
    # "ru",  # TODO: need transliteration
    "pt",
    # "ur",  # TODO: need transliteration
    "id",
    "de",
    # "ja",  # TODO: need transliteration
    # "te",  # TODO: need transliteration
    "tr",
    # "ta",  # TODO: need transliteration
    # "ko",  # TODO: need transliteration
    "vi",
    "it",
    # "th",  # TODO: need transliteration
    "tl",
    "zh_tw",
    # "fa",  # TODO: need transliteration
    "zh_cn",
}


def process_str(s):
    """
    Process a string for string comparison.
    - lowercase it
    - replace special characters (e.g. accents) with their ASCII equivalents
    """
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s


# 2. Load all interla tokens
def get_int_orth_tokens():
    interla_df = pd.read_csv("output/pronounceable_combinations.csv")
    int_orth_tokens = list(set(interla_df["word"].tolist()))

    print(len(int_orth_tokens), "interla orthographied tokens")
    return int_orth_tokens


int_orth_tokens = get_int_orth_tokens()

# 3. Collect all "et" words and their associated words from all other languages


def step_1():
    # FIXME: ~30s long

    # 1. Load all pkl files from data/translations/downloads/xx-yy.pkl if yy is "et"
    pkl_dir = "data/translations/downloads"
    pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
    et_pkls = [
        f
        for f in pkl_files
        if os.path.basename(f)[:2] == "et" and os.path.basename(f)[-6:-4] in TO_KEEP
    ]

    # TODO: ALSO USE os.path.basename(f)[:2] == "et"

    _, LANG_WEIGHTS = get_lang_weights()
    min_weight = min(LANG_WEIGHTS.values())
    LANG_WEIGHTS = defaultdict(lambda: min_weight, LANG_WEIGHTS)

    int_anon_tokens_coocurrences = dict()  # 156: {"fi": [159, 8], "sv": [2, 8]}
    all_y2normWord = dict()  # To collect all y2word mappings
    all_y2word = dict()  # To collect all y2word mappings
    all_word2x = dict()  # To collect all word2x mappings

    for fpath in tqdm(et_pkls):
        lang2 = os.path.basename(fpath)[-6:-4]  # e.g. "fi" from "et-fi.pkl"

        with open(fpath, "rb") as f:
            word2x, y2word, x2ys = pickle.load(f)
            x2word = {
                v: k for k, v in word2x.items()
            }  # Reverse mapping: id -> word in lang1
            # word2x is a dict: word -> id in lang1
            # y2word is a dict: id -> word in lang2
            # x2ys is a dict: id in lang1 -> list of ids in lang2

        y2normWord = {k: process_str(v) for k, v in y2word.items()}
        all_y2normWord[lang2] = y2normWord  # Collect all y2word mappings
        all_y2word[lang2] = y2word

        # TODO: WE ASSUME THERE ARE RANKED BY FREQUENCY
        for x_id, ys in list(x2ys.items())[:N]:  # Limit to N to match interla tokens
            # reindex x_id
            word = x2word.get(x_id)
            if word in all_word2x:
                new_x_id = all_word2x[word]
            else:
                new_x_id = len(all_word2x)
                all_word2x[word] = new_x_id

            int_anon_tokens_coocurrences.setdefault(new_x_id, dict())
            # int_anon_tokens_coocurrences[x_id][lang2] = ys[:3]
            int_anon_tokens_coocurrences[new_x_id][lang2] = ys[0]

    print(len(int_anon_tokens_coocurrences), "interla anonymous tokens")
    return int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS


int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()


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
