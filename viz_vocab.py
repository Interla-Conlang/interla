import os
import pickle
from typing import Dict

from assign_spellings_common import IPAProcessor, step_1
from constants import LANG_TO_EPITRAN
from str_barycenter import align_words_list
from utils import ALL_VALID_LANGUAGES


def viz_vocab():
    int_anon_tokens_coocurrences, all_y2normWord, all_y2word, _ = step_1()

    ipa_processors = {
        lang: IPAProcessor(lang, replace=False)
        for lang in ALL_VALID_LANGUAGES
        if LANG_TO_EPITRAN[lang] is not None
    }

    interla_vocab_path = "output/interla_vocab.pkl"

    if os.path.exists(interla_vocab_path):
        with open(interla_vocab_path, "rb") as f:
            vocab: Dict[str, str] = pickle.load(f)
    else:
        return

    for int_orth_token, int_anon_token in vocab.items():
        assoc_words = int_anon_tokens_coocurrences.get(int_anon_token, {})
        if len(assoc_words) > 5 and (
            "en" in assoc_words or "fr" in assoc_words
        ):  # easier to understand for me
            print(f"Interla: {int_orth_token}")
            items = sorted(
                assoc_words.items(),
                key=lambda x: x[0],  # sort alphabetically by language code
            )
            words = [all_y2word[lang][y_id] for lang, y_id in items]
            normWords = [all_y2normWord[lang][y_id] for lang, y_id in items]
            ipas = [
                ipa_processors[lang].process_str(word)
                for (lang, _), word in zip(items, words)
            ]
            for word, normWord, ipa, (lang, _) in zip(words, normWords, ipas, items):
                print(f"  {lang}:\t{word}\t/{ipa}/\t({normWord})")

            for line in align_words_list(normWords):
                print(line)
            input()


if __name__ == "__main__":
    viz_vocab()
