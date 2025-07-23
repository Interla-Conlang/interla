"""
Constants
"""

from typing import Dict, Optional

# Language code mapping from your TO_KEEP codes to epitran codes
LANG_TO_EPITRAN: Dict[str, Optional[str]] = {
    "ja": "jpn-Hrgn",  # Japanese (Hiragana)
    "es": "spa-Latn",  # Spanish
    "de": "deu-Latn",  # German
    "br": None,  # No match (could be Breton: "bre-Latn" but not in list)
    "ka": None,  # No match (could be Georgian: "kat-Geor" but not in list)
    "gl": None,  # Galician (not in provided list, fallback ERROR)
    "el": None,  # Greek (not in provided list, fallback ERROR)
    "nl": "nld-Latn",  # Dutch
    "te": "tel-Telu",  # Telugu
    "ms": "msa-Latn",  # Malay
    "kk": "kaz-Cyrl",  # Kazakh (Cyrillic)
    "lv": None,  # No match (Latvian: "lav-Latn" not in list)
    "da": None,  # No match (Danish: "dan-Latn" not in list)
    "ta": "tam-Taml",  # Tamil
    "fi": None,  # Finnish (not in provided list, fallback ERROR)
    "en": "eng-Latn",  # English
    "is": None,  # No match (Icelandic: "isl-Latn" not in list)
    "eu": None,  # Basque (not in provided list, fallback ERROR)
    "th": "tha-Thai",  # Thai
    "ca": "cat-Latn",  # Catalan
    "zh_cn": "cmn-Hans",  # Mandarin (Simplified)
    "hy": None,  # No match (Armenian: "hye-Armn" not in list)
    "af": "aar-Latn",  # Afar
    "si": "sin-Sinh",  # Sinhala
    "it": "ita-Latn",  # Italian
    "lt": None,  # No match (Lithuanian: "lit-Latn" not in list)
    "tl": "tgl-Latn",  # Tagalog
    "ro": "ron-Latn",  # Romanian
    "ze_zh": None,  # No match
    "uk": "ukr-Cyrl",  # Ukrainian
    "hr": "hrv-Latn",  # Croatian
    "ru": "rus-Cyrl",  # Russian
    "sv": "swe-Latn",  # Swedish
    "sk": "ces-Latn",  # Czech (Slovak: "slk-Latn" not in list)
    "vi": "vie-Latn",  # Vietnamese
    "sr": "srp-Latn",  # Serbian
    "ko": "kor-Hang",  # Korean
    "bs": None,  # No match (Bosnian: "bos-Latn" not in list)
    "id": "ind-Latn",  # Indonesian
    "hu": "hun-Latn",  # Hungarian
    "tr": "tur-Latn",  # Turkish
    "ar": "ara-Arab",  # Arabic
    "sl": None,  # No match (Slovenian: "slv-Latn" not in list)
    "no": None,  # No match (Norwegian: "nor-Latn" not in list)
    "cs": "ces-Latn",  # Czech
    "zh_tw": "cmn-Hant",  # Mandarin (Traditional)
    "ml": "mal-Mlym",  # Malayalam
    "pt_br": "por-Latn",  # Brazilian Portuguese (use Portuguese)
    "sq": "sqi-Latn",  # Albanian
    "pl": "pol-Latn",  # Polish
    "hi": "hin-Deva",  # Hindi
    "bn": "ben-Beng",  # Bengali
    "bg": None,  # No match (Bulgarian: "bul-Cyrl" not in list)
    "fr": "fra-Latn",  # French
    "ur": "urd-Arab",  # Urdu
    "eo": "epo-Latn",  # Esperanto
    "mk": None,  # No match (Macedonian: "mkd-Cyrl" not in list)
    "fa": "fas-Arab",  # Farsi
    "pt": "por-Latn",  # Portuguese
    "he": None,  # No match (Hebrew: "heb-Hebr" not in Epitran list)
}
