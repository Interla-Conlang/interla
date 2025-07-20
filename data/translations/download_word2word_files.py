import os

import requests


def get_download_url(lang1, lang2):
    return f"https://mk.kakaocdn.net/dn/kakaobrain/word2word/{lang1}-{lang2}.pkl"


def download_pkl(lang1, lang2, save_dir="data/translations/downloads"):
    url = get_download_url(lang1, lang2)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{lang1}-{lang2}.pkl")
    if os.path.exists(save_path):
        print(f"File {save_path} already exists. Skipping download.")
        return
    print(f"Downloading {url} ...")
    r = requests.get(url)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(r.content)
        print(f"Saved to {save_path}")
    else:
        print(f"Failed to download {url} (status code: {r.status_code})")


def main():
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "supporting_languages.txt"
    )
    with open(filepath, "r") as f:
        for line in f:
            pair = line.strip()
            if not pair or "-" not in pair:
                continue
            lang1, lang2 = pair.split("-")
            download_pkl(lang1, lang2)


if __name__ == "__main__":
    main()
