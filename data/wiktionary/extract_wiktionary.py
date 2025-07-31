"""
Download and preprocess (to reduce filesize) JSONL file extracted from Wiktionary.
"""

import json
import os
import subprocess

from tqdm import tqdm

KEYS_TO_DROP = {
    "lang",  # 'lang' = 'Français'
    "pos_title",  # 'pos_title' = 'Nom commun'
    "etymology_texts",
    "etymology_text",
    "etymology_templates",
    "senses",
    "anagrams",
    "categories",
    "meronyms",
    "hypernyms",
    "hyponyms",
    "holonyms",
    "notes",
    "proverbs",
    "paronyms",
    "etymology_examples",
    "troponyms",
    "coordinate_terms",
    "etymology_number",
    "wikipedia",
    "original_title",
    "wikidata",
    "source",
    "descendants",
    "info_templates",
    "head_templates",
    "inflection_templates",
    "literal_meaning",
}

KEYS_TO_KEEP = {
    "word",
    "lang_code",
    "pos",
    "forms",
    "sounds",
    "translations",
    "synonyms",
    "derived",
    "related",
    "tags",
    "raw_tags",
    "antonyms",
    "abbreviation",
    "title",
    "redirect",
    "redirects",
    "form_of",
    "alt_of",
    "hyphenation",
    "abbreviations",
    "instances",
    "hyphenations",
}

KNOWN_KEYS = KEYS_TO_DROP.union(KEYS_TO_KEEP)

# Get number of lines in the JSONL file using a shell command

jsonl_paths = [
    "data/wiktionary/fr-extract.jsonl",
    "data/wiktionary/kaikki.org-dictionary-all-words.jsonl.gz",
]


def process_jsonl(path: str) -> None:
    if path.endswith(".gz"):
        jsonl_path = path[:-3]
    else:
        jsonl_path = path
    light_jsonl_path = jsonl_path.replace(".jsonl", ".light.jsonl")

    if os.path.exists(light_jsonl_path):
        print(f"Skipping {path}, already processed.")
        return

    # First unzip the file using a shell command
    if path.endswith(".gz"):
        if not os.path.exists(jsonl_path):
            subprocess.run(["gunzip", path], check=True)
    # TODO: this deletes the original file, but we might want to keep it...

    n = int(subprocess.check_output(["wc", "-l", jsonl_path]).split()[0])

    # TODO: do not unzip the file, open it directly with gzip
    with (
        open(jsonl_path, "r", encoding="utf-8") as f,
        open(light_jsonl_path, "w", encoding="utf-8") as out_f,
    ):
        for line in tqdm(f, total=n, desc="Processing JSONL lines"):
            data = json.loads(line)

            # Filter to keep only the desired keys
            filtered_data = {
                key: value for key, value in data.items() if key in KEYS_TO_KEEP
            }

            # Keep only key 'ipa' for all 'sounds' (we don't care about rhymes or audio files)
            # if "sounds" in filtered_data:
            #     filtered_data["sounds"] = list(set(
            #         sound["ipa"].replace("\\", "")
            #         for sound in filtered_data["sounds"]
            #         if "ipa" in sound
            #     ))
            # TODO: for the moment we only keep first IPA value
            if "sounds" in filtered_data:
                ipa = [
                    sound["ipa"].replace("\\", "").replace("/", "")
                    for sound in filtered_data["sounds"]
                    if "ipa" in sound
                ][:1]
                if ipa:
                    filtered_data["ipa"] = ipa[0]
                del filtered_data["sounds"]

            # Keep only 'lang_code', 'word', 'sense', 'sense_index', and 'tags' for translations
            if "translations" in filtered_data:
                ts = []
                for t in filtered_data["translations"]:
                    d = {}
                    if "lang_code" in t:
                        d["lang_code"] = t["lang_code"]
                    elif "code" in t:
                        d["lang_code"] = t["code"]
                    if "word" in t:
                        d["word"] = t["word"]
                    if "sense_index" in t:
                        d["sense_index"] = t["sense_index"]
                    if "tags" in t:
                        d["tags"] = t["tags"]  # neuter, feminine, masculine, etc.
                    ts.append(d)
                filtered_data["translations"] = ts

            # In synonyms, keep only 'word'
            if "synonyms" in filtered_data:
                filtered_data["synonyms"] = list(
                    set(
                        syn["word"]
                        for syn in filtered_data["synonyms"]
                        if "word" in syn
                    )
                )

            # If derived forms are present, keep only 'word'
            if "derived" in filtered_data:
                filtered_data["derived"] = list(
                    set(
                        form["word"]
                        for form in filtered_data["derived"]
                        if "word" in form
                    )
                )

            # If related words are present, keep only 'word'
            if "related" in filtered_data:
                filtered_data["related"] = list(
                    set(
                        rel["word"] for rel in filtered_data["related"] if "word" in rel
                    )
                )

            # Write the filtered data to the output file
            out_f.write(json.dumps(filtered_data, ensure_ascii=False) + "\n")

            # TO KEEP
            # 'word' = 'accueil'
            # 'lang_code' = 'fr'
            # 'pos' = 'noun'
            # 'forms': [{'form': 'accueils', 'tags': [...]}]
            # 'translations': [{'lang_code': 'de', 'lang': 'Allemand', 'word': 'Aufnahme', 'sense': 'Cérémonie', 'sense_index': 1, 'tags': ['feminine']}, 005: {'lang_code': 'ar', 'lang': 'Arabe', 'word': 'إِسْتِقْبَال', 'sense': 'Cérémonie', 'sense_index': 1, 'roman': 'istiqbèl'} {014: {'lang_code': 'cmn', 'lang': 'Mandarin', 'word': '迎接', 'sense': 'Cérémonie', 'sense_index': 1, 'roman': 'yíngjiē', 'traditional_writing': '迎接'}, ...]
            # 'synonyms': [{'word': 'home', 'tags': [...], 'sense': 'site web'}, {'word': 'main page', 'tags': [...], 'sense': 'site web'}, {'word': 'page d’accueil', 'sense': 'site web'}]
            # 'derived': [{'word': 'accueil de loisirs'}, {'word': 'agent d’accueil'}, {'word': 'comité d’accueil'}, {'word': 'émission d’accueil'}, {'word': 'faire bon accueil'}, {'word': 'faire mauvais accueil'}, {'word': 'famille d’accueil'}, {'word': 'multi-accueils'}, {'word': 'page d’accueil'}, {'word': 'plage d’accueil'}, {'word': 'station d’accueil'}]
            # 'related': [{'word': 'accueillir'}, {'word': 'accueillage'}, {'word': 'accueillant'}]
            # 'tags': ['masculine']
            # 'raw_tags': ['3ᵉ groupe']
            # 'antonyms': [{'word': 'dur', 'sense_index': 1}, {'word': 'solide', 'sense_index': 1}, {'word': 'immeuble', 'sense_index': 2}]
            # 'abbreviation': [{'word': 'mar.'}]
            # instances, value: [{'word': 'January', 'source': 'Thesaurus:month'}, ...]
            # Unknown key: hyphenations, value: [{'parts': ['dic', 'tion', 'a', 'ry']}, {'parts': ['dic', 'tion', 'ary']}]
            # Unknown key: alt_of, value: [{'word': 'bə́ wə́'}]
            # Unknown key: form_of, value: [{'word': 'tu'}]

            # REDIRECTS
            # 'title' = "quelqu'un"
            # 'redirect' = "quelqu’un"
            # 'pos' = "hard-redirect"

            # TODO: dois-je inclure dans l'optimisation?
            # "meronyms",
            # "hypernyms",
            # "hyponyms",
            # holonyms
            # 'troponyms'

            # for key in data:
            #     if key not in known_keys:
            #         print(f"Unknown key: {key}, value: {data[key]}")
            #         known_keys.add(key)

    # Delete the original JSONL file if it was gzipped
    # if path.endswith(".gz"):
    #     os.remove(jsonl_path)


if __name__ == "__main__":
    for jsonl_path in jsonl_paths:
        process_jsonl(jsonl_path)
