import pickle

from tqdm import tqdm

from assign_spellings_common import step_1
from str_barycenter import string_barycenter

int_anon_tokens_coocurrences, all_y2normWord, all_y2word, LANG_WEIGHTS = step_1()

vocab = {}

for int_anon_token, assoc_words in tqdm(
    int_anon_tokens_coocurrences.items(), desc="Finding optimal interla tokens"
):
    words = [all_y2normWord[lang].get(w_id, "") for lang, w_id in assoc_words.items()]
    if len(words) == 1:
        int_orth_token = words[0]
    else:
        int_orth_token = string_barycenter(words)

    vocab[int_orth_token] = int_anon_token

# Save the vocabulary to a pickle file

with open("output/interla_vocab.pkl", "wb") as f:
    pickle.dump(vocab, f)


for int_orth_token, int_anon_token in vocab.items():
    assoc_words = int_anon_tokens_coocurrences.get(int_anon_token, {})
    print(f"Interla: {int_orth_token}")
    for lang, y_id in assoc_words.items():
        y2word = all_y2word.get(lang, {})
        word = y2word.get(y_id, "")
        print(f"  {lang}: {word}")
    print()
