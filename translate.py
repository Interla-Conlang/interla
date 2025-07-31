import argparse
import logging
import os
import pickle
from typing import Dict

from assign_spellings_common import get_data_from_opensub


def load_vocab(vocab_path: str) -> Dict[str, int]:
    with open(vocab_path, "rb") as f:
        return pickle.load(f)


def build_lang_to_interla(
    target_lang, vocab, int_anon_tokens_cooccurrences, all_y2word
):
    lang_to_interla = {}
    if target_lang not in all_y2word:
        logging.warning(f"Language {target_lang} not found in available languages")
        return lang_to_interla
    y2word = all_y2word[target_lang]
    for int_orth_token, int_anon_token in vocab.items():
        assoc_words = int_anon_tokens_cooccurrences.get(int_anon_token, {})
        if target_lang in assoc_words:
            y_id = assoc_words[target_lang]
            word = y2word[y_id]
            lang_to_interla[word] = int_orth_token
    return lang_to_interla


def translate_text(text: str, lang_to_interla: Dict[str, str]) -> str:
    words = text.strip().split()
    translated = [lang_to_interla.get(word, word) for word in words]
    return " ".join(translated)


def main():
    parser = argparse.ArgumentParser(
        description="Translate text from a given language to Interla."
    )
    parser.add_argument(
        "-l", "--lang", default="en", help="Source language code (default: en)"
    )
    parser.add_argument("-t", "--text", required=True, help="Text to translate")
    args = parser.parse_args()

    int_anon_tokens_cooccurrences, _, all_y2word, _ = get_data_from_opensub()
    interla_vocab_path = "output/interla_vocab.pkl"
    if not os.path.exists(interla_vocab_path):
        print(f"Interla vocabulary file not found at {interla_vocab_path}")
        return

    vocab = load_vocab(interla_vocab_path)
    lang_to_interla = build_lang_to_interla(
        args.lang, vocab, int_anon_tokens_cooccurrences, all_y2word
    )
    if not lang_to_interla:
        print(f"No translation dictionary found for language {args.lang}")
        return

    translated = translate_text(args.text, lang_to_interla)
    print(translated)


if __name__ == "__main__":
    main()
