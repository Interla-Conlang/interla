"""
Download and preprocess (to reduce filesize) JSONL file extracted from Wiktionary.
"""

import gzip
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from multiprocessing import cpu_count

import orjson
from tqdm import tqdm


def json_loads(s):
    return orjson.loads(s)


def json_dumps(obj):
    return orjson.dumps(obj).decode("utf-8")


# Pre-compile translation table for string cleaning
IPA_CLEAN_TRANS = str.maketrans("", "", "\\/")

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


def process_line(line: str) -> str:
    """Process a single line of JSONL data."""
    data = json_loads(line)

    # Filter to keep only the desired keys
    filtered_data = {key: value for key, value in data.items() if key in KEYS_TO_KEEP}

    # Keep only key 'ipa' for all 'sounds' (we don't care about rhymes or audio files)
    if "sounds" in filtered_data:
        for sound in filtered_data["sounds"]:
            if "ipa" in sound:
                # Use str.translate for faster string cleaning
                filtered_data["ipa"] = sound["ipa"].translate(IPA_CLEAN_TRANS)
                break
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

    # Extract 'word' from lists
    for key in ["synonyms", "derived", "related"]:
        if key in filtered_data:
            words = {item["word"] for item in filtered_data[key] if "word" in item}
            filtered_data[key] = list(words)

    return json_dumps(filtered_data)


def process_chunk(lines: list[str]) -> list[str]:
    """Process a chunk of lines."""
    return [process_line(line.strip()) for line in lines if line.strip()]


def get_line_count_fast(file_path: str) -> int:
    """Fast line counting without shell command."""
    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            return sum(1 for _ in f)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)


def process_jsonl(path: str) -> None:
    """Process JSONL file with multiprocessing and optimizations."""
    light_jsonl_path = path.replace(".jsonl.gz", ".light.jsonl").replace(
        ".jsonl", ".light.jsonl"
    )

    if os.path.exists(light_jsonl_path):
        print(f"Skipping {path}, already processed.")
        return

    print(f"Processing {path}...")

    # Determine chunk size and number of workers
    chunk_size = 50_000  # Fixed chunk size
    num_workers = min(cpu_count(), 10)  # Limit to 10 workers max

    print(f"Using {num_workers} workers with chunk size {chunk_size}")

    # Open input file (gzipped or regular)
    if path.endswith(".gz"):
        input_file = gzip.open(path, "rt", encoding="utf-8")
    else:
        input_file = open(path, "r", encoding="utf-8")

    processed_lines = 0  # Initialize here to avoid unbound variable
    try:
        with (
            input_file,
            open(light_jsonl_path, "w", encoding="utf-8", buffering=8192 * 8) as out_f,
        ):
            # Process in chunks using multiprocessing
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                chunk = []

                # Use tqdm for progress tracking
                with tqdm(desc="Processing lines") as pbar:
                    for line in input_file:
                        chunk.append(line)

                        if len(chunk) >= chunk_size:
                            # Submit chunk for processing
                            future = executor.submit(process_chunk, chunk.copy())
                            futures.append(future)
                            chunk.clear()

                            # Write completed chunks to maintain order
                            while futures and futures[0].done():
                                completed_future = futures.pop(0)
                                results = completed_future.result()
                                for result in results:
                                    out_f.write(result + "\n")
                                processed_lines += len(results)
                                pbar.update(len(results))

                    # Process remaining chunk
                    if chunk:
                        future = executor.submit(process_chunk, chunk)
                        futures.append(future)

                    # Process remaining futures
                    for future in as_completed(futures):
                        results = future.result()
                        for result in results:
                            out_f.write(result + "\n")
                        processed_lines += len(results)
                        pbar.update(len(results))

    finally:
        input_file.close()

        print(f"Processed {processed_lines:,} lines and saved to {light_jsonl_path}")


if __name__ == "__main__":
    for jsonl_path in jsonl_paths:
        process_jsonl(jsonl_path)

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
