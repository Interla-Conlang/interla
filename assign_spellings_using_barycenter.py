import os
import pickle
from typing import Dict, Tuple

from tqdm.contrib.concurrent import process_map

from assign_spellings_common import step_1
from str_barycenter import string_barycenter
from utils import IPA_TO_INTERLA

int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()

interla_vocab_path = "output/interla_vocab.pkl"

if os.path.exists(interla_vocab_path):
    with open(interla_vocab_path, "rb") as f:
        vocab: Dict[str, str] = pickle.load(f)
else:
    vocab = {}

    def compute_token(args: Tuple[str, dict]) -> Tuple[str, str]:
        """
        Compute the interlanguage token for a given anonymous token and its associated words.
        Function used for parallel processing.
        Args:
            args (Tuple[str, dict]): A tuple containing the anonymous token and a dictionary
                mapping language codes to word IDs associated with that token.
        Returns:
            Tuple[str, str]: A tuple containing the interlanguage orthographic token and the anonymous token
            for which it was computed.
        """
        int_anon_token, assoc_words = args

        # Get the words and the weights
        words = [
            all_y2normWord[lang].get(w_id, "") for lang, w_id in assoc_words.items()
        ]
        weights = [LANG_WEIGHTS[lang] for lang in assoc_words.keys()]

        to_keep = [bool(len(word)) for word in words]
        words = [word for word, keep in zip(words, to_keep) if keep]
        weights = [weight for weight, keep in zip(weights, to_keep) if keep]

        # Compute barycenter
        if len(words) == 0:
            int_ipa_token = ""
        elif len(words) == 1:
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
        # chunksize=1
    )
    for int_orth_token, int_anon_token in results:
        if int_orth_token:  # remove empty tokens
            vocab[int_orth_token] = int_anon_token

    # Save the vocabulary to a pickle file
    with open(interla_vocab_path, "wb") as f:
        pickle.dump(vocab, f)
