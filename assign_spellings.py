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
from difflib import SequenceMatcher

import networkx as nx
import pandas as pd
from tqdm import tqdm

# 1. Load all pkl files from data/translations/downloads/xx-yy.pkl if yy is "et"
pkl_dir = "data/translations/downloads"
pkl_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
et_pkls = [f for f in pkl_files if os.path.basename(f)[:2] == "et"]
# TODO: ALSO USE os.path.basename(f)[:2] == "et"

# 2. Collect all "et" words and their associated words from all other languages
# TODO: 1mn long
int_anon_tokens_coocurrences = dict()  # 156: {"fi": [159, 8], "sv": [2, 8]}
all_y2word = dict()  # To collect all y2word mappings

for fpath in tqdm(et_pkls):
    lang1 = os.path.basename(fpath)[:2]  # e.g. "et" from "et-fi.pkl"
    lang2 = os.path.basename(fpath)[-6:-4]  # e.g. "fi" from "et-fi.pkl"

    with open(fpath, "rb") as f:
        word2x, y2word, x2ys = pickle.load(f)
        # word2x is a dict: word -> id in lang1
        # y2word is a dict: id -> word in lang2
        # x2ys is a dict: id in lang1 -> list of ids in lang2

    all_y2word[lang2] = y2word  # Collect all y2word mappings

    for x_id, ys in x2ys.items():
        int_anon_tokens_coocurrences.setdefault(x_id, dict())
        int_anon_tokens_coocurrences[x_id][lang2] = ys

# 3. Load all interla tokens
interla_df = pd.read_csv("output/pronounceable_combinations.csv")
int_orth_tokens = interla_df["word"].tolist()

# 4. Build bipartite graph
G = nx.Graph()
A = set(int_orth_tokens)
B = set(int_anon_tokens_coocurrences.keys())

G.add_nodes_from(A, bipartite=0)
G.add_nodes_from(B, bipartite=1)


def normalized_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# 5. Add weighted edges
for interla_token in A:
    for et_word, assoc_words in int_anon_tokens_coocurrences.items():
        if not assoc_words:
            continue
        sims = []
        for lang, ids in assoc_words.items():
            y2word = all_y2word.get(lang, {})
            for y_id in ids:
                w = y2word.get(y_id)
                if w is not None:
                    sims.append(normalized_similarity(interla_token, w))
        avg_sim = sum(sims) / len(sims)
        G.add_edge(interla_token, et_word, weight=avg_sim)

# Now G is the bipartite graph as described
# You can save or process G as needed, e.g.:
# nx.write_gpickle(G, "output/interla_et_bipartite_graph.gpickle")
