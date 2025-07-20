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
from collections import defaultdict

import networkx as nx
import pandas as pd
from rapidfuzz import fuzz
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from utils import get_lang_weights

_, LANG_WEIGHTS = get_lang_weights()
min_weight = min(LANG_WEIGHTS.values())
LANG_WEIGHTS = defaultdict(lambda: min_weight, LANG_WEIGHTS)

N = 2_000

# 1. Load all pkl files from data/translations/downloads/xx-yy.pkl if yy is "et"
pkl_dir = "data/translations/downloads"
pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
et_pkls = [f for f in pkl_files if os.path.basename(f)[:2] == "et"]
# TODO: ALSO USE os.path.basename(f)[:2] == "et"

# 2. Load all interla tokens
interla_df = pd.read_csv("output/pronounceable_combinations.csv")
int_orth_tokens = set(interla_df["word"].tolist())

print(len(int_orth_tokens), "interla tokens with et words")

# 3. Collect all "et" words and their associated words from all other languages
# TODO: 30s long
int_anon_tokens_coocurrences = dict()  # 156: {"fi": [159, 8], "sv": [2, 8]}
all_y2word = dict()  # To collect all y2word mappings

for fpath in tqdm(et_pkls):
    lang2 = os.path.basename(fpath)[-6:-4]  # e.g. "fi" from "et-fi.pkl"

    with open(fpath, "rb") as f:
        _, y2word, x2ys = pickle.load(f)
        # word2x is a dict: word -> id in lang1
        # y2word is a dict: id -> word in lang2
        # x2ys is a dict: id in lang1 -> list of ids in lang2

    all_y2word[lang2] = y2word  # Collect all y2word mappings

    for x_id, ys in list(x2ys.items())[:N]:  # Limit to N to match interla tokens
        int_anon_tokens_coocurrences.setdefault(x_id, dict())
        int_anon_tokens_coocurrences[x_id][lang2] = ys[:3]

print(len(int_anon_tokens_coocurrences), "interla tokens with et words")

# 4. Build bipartite graph
G = nx.Graph()
A = set(int_orth_tokens)
B = set(int_anon_tokens_coocurrences.keys())

G.add_nodes_from(A, bipartite=0)
G.add_nodes_from(B, bipartite=1)


def normalized_similarity(a, b):
    return fuzz.ratio(a, b) / 100


# for int_orth_token in tqdm(A):
def process_int_orth_token(int_orth_token):
    for int_anon_token, assoc_words in int_anon_tokens_coocurrences.items():
        distances = dict()
        for lang, ids in assoc_words.items():
            dists = []
            y2word = all_y2word.get(lang, {})
            for y_id in ids:
                w = y2word.get(y_id)
                if w is not None:
                    distance = 1 - normalized_similarity(int_orth_token, w)
                    dists.append(distance)
            if dists:
                avg_dist = sum(dists) / len(dists)
                distances[lang] = avg_dist

        # Compute weighted average distance, renormalized to sum to 1
        total_weight = sum(LANG_WEIGHTS[lang] for lang in distances)
        if total_weight > 0:
            avg_dist = (
                sum(distances[lang] * LANG_WEIGHTS[lang] for lang in distances)
                / total_weight
            )
            G.add_edge(int_orth_token, int_anon_token, weight=avg_dist)


thread_map(process_int_orth_token, A, max_workers=32)

# Now G is the bipartite graph as described
nx.write_gpickle(G, "output/interla_et_bipartite_graph.gpickle")

# Compute the minimum weight full matching (maximum weight matching with negated weights)
matching = nx.algorithms.bipartite.matching.minimum_weight_full_matching(
    G, weight="weight"
)

# Save the matching to a file
with open("output/interla_et_matching.pkl", "wb") as f:
    pickle.dump(matching, f)

# Then display the words from A with all their associated "w = y2word.get(y_id)"
for int_orth_token in A:
    int_anon_token = matching[int_orth_token]
    assoc_words = int_anon_tokens_coocurrences.get(int_anon_token, {})
    print(f"Interla: {int_orth_token} <-> et: {int_anon_token}")
    for lang, ids in assoc_words.items():
        y2word = all_y2word.get(lang, {})
        words = [y2word.get(y_id, "") for y_id in ids]
        print(f"  {lang}: {', '.join(words)}")
    print()
