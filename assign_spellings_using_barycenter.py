import os
import pickle

from tqdm.contrib.concurrent import process_map

from assign_spellings_common import step_1
from str_barycenter import string_barycenter
from utils import IPA_TO_INTERLA

int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()

interla_vocab_path = "output/interla_vocab.pkl"

if os.path.exists(interla_vocab_path):
    with open(interla_vocab_path, "rb") as f:
        vocab = pickle.load(f)
else:
    vocab = {}

    def compute_token(args):
        int_anon_token, assoc_words = args

        # Get the words and the weights
        words = [
            all_y2normWord[lang].get(w_id, "") for lang, w_id in assoc_words.items()
        ]
        weights = [LANG_WEIGHTS[lang] for lang in assoc_words.keys()]

        # Compute barycenter
        if len(words) == 1:
            int_ipa_token = words[0]
        else:
            int_ipa_token = string_barycenter(words, weights)

        # Convert back from IPA to orthography
        int_orth_token = "".join(IPA_TO_INTERLA[char] for char in int_ipa_token)

        return int_orth_token, int_anon_token

    results = process_map(
        compute_token,
        list(int_anon_tokens_coocurrences.items()),
        desc="Finding optimal interla tokens",
    )
    for int_orth_token, int_anon_token in results:
        vocab[int_orth_token] = int_anon_token

    # Save the vocabulary to a pickle file
    with open(interla_vocab_path, "wb") as f:
        pickle.dump(vocab, f)


for int_orth_token, int_anon_token in vocab.items():
    assoc_words = int_anon_tokens_coocurrences.get(int_anon_token, {})
    if len(assoc_words) > 5:
        print(f"Interla: {int_orth_token}")
        for lang, y_id in assoc_words.items():
            y2word = all_y2word.get(lang, {})
            y2normWord = all_y2normWord.get(lang, {})
            word = y2word.get(y_id, "")
            normWord = y2normWord.get(y_id, "")
            print(f"  {lang}: {word} ({normWord})")
        print()
