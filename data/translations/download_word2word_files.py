import os
from collections import Counter

import requests
from tqdm.contrib.concurrent import thread_map


def get_download_url(lang1, lang2):
    return f"https://mk.kakaocdn.net/dn/kakaobrain/word2word/{lang1}-{lang2}.pkl"


def download_pkl(pair, save_dir="data/translations/downloads"):
    lang1, lang2 = pair
    if lang1 != "et" and lang2 != "et":
        return
    url = get_download_url(lang1, lang2)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{lang1}-{lang2}.pkl")
    if os.path.exists(save_path):
        print(f"File {save_path} already exists. Skipping download.")
        return
    print(f"Downloading {url} ...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(r.content)
                print(f"Saved to {save_path}")
                break
            else:
                print(f"Failed to download {url} (status code: {r.status_code})")
                break
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError) as e:
            print(f"Download failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"Giving up on {url}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            if attempt == max_retries - 1:
                print(f"Giving up on {url}")


def main():
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "supporting_languages.txt"
    )
    pairs = []
    with open(filepath, "r") as f:
        for line in f:
            pair = line.strip()
            if not pair or "-" not in pair:
                continue
            lang1, lang2 = pair.split("-")
            pairs.append((lang1, lang2))
    thread_map(download_pkl, pairs, max_workers=8, desc="Downloading files")


def count_languages(filepath=None):
    if filepath is None:
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "supporting_languages.txt"
        )
    lang_counter = Counter()
    with open(filepath, "r") as f:
        for line in f:
            pair = line.strip()
            if not pair or "-" not in pair:
                continue
            lang1, lang2 = pair.split("-")
            lang_counter[lang1] += 1
            lang_counter[lang2] += 1
    # Order the counter by count descending
    return Counter(dict(lang_counter.most_common()))


if __name__ == "__main__":
    # lang_counter = count_languages()
    # print("Language counts:")
    # for lang, count in lang_counter.items():
    #     print(f"{lang}: {count}")
    main()
