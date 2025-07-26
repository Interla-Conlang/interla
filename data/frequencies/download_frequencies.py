import os
import requests

"""
https://github.com/oprogramador/most-common-words-by-language
"""

URLS = {
    lang: f"https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/{lang}/{lang}_50k.txt"
    for lang in [
        "af",
        "ar",
        "bg",
        "bn",
        "br",
        "bs",
        "ca",
        "cs",
        "da",
        "de",
        "el",
        "en",
        "eo",
        "es",
        "et",
        "eu",
        "fa",
        "fi",
        "fr",
        "gl",
        "he",
        "hi",
        "hr",
        "hu",
        "hy",
        "id",
        "is",
        "it",
        "ja",
        "ka",
        "kk",
        "ko",
        "lt",
        "lv",
        "mk",
        "ml",
        "ms",
        "nl",
        "no",
        "pl",
        "pt",
        "pt_br",
        "ro",
        "ru",
        "si",
        "sk",
        "sl",
        "sq",
        "sr",
        "sv",
        "ta",
        "te",
        "th",
        "tl",
        "tr",
        "uk",
        "vi",
        "zh",
        "zh_tw",
    ]
}
output_dir = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(output_dir, exist_ok=True)

for lang, url in URLS.items():
    out_path = os.path.join(output_dir, f"{lang}.txt")
    print(f"Downloading {lang} from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(response.content)
    print(f"Saved to {out_path}")