"""
Constants
"""

from typing import Dict, Optional

# Language code mapping from your TO_KEEP codes to epitran codes
OPENSUB_LANGS_TO_EPITRAN: Dict[str, Optional[str]] = {
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

WIKTIONARY_LANGS_TO_EPITRAN: Dict[str, Optional[str]] = {
    "bcl": None,  # Bikol Central (not in Epitran list)
    "mr": "mar-Deva",  # Marathi
    "am": "amh-Ethi",  # Amharic
    "nv": None,  # Navajo (not in Epitran list)
    "my": "mya-Mymr",  # Burmese/Myanmar
    "it": "ita-Latn",  # Italian
    "lmo": None,  # Lombard (not in Epitran list)
    "oc": None,  # Occitan (not in Epitran list)
    "ro": "ron-Latn",  # Romanian
    "tab": None,  # Tabasaran (not in Epitran list)
    "smn": None,  # Inari Sami (not in Epitran list)
    "wls": None,  # Wallisian (not in Epitran list)
    "tg": "tgk-Cyrl",  # Tajik
    "az": "aze-Latn",  # Azerbaijani (Latin)
    "ne": None,  # Nepali (not in Epitran list)
    "sw": "swa-Latn",  # Swahili
    "nap": None,  # Neapolitan (not in Epitran list)
    "mi": "mri-Latn",  # Maori
    "ckb": "ckb-Arab",  # Sorani Kurdish
    "mfe": None,  # Morisyen (not in Epitran list)
    "pga": None,  # Juba Arabic (not in Epitran list)
    "moe": None,  # Montagnais (not in Epitran list)
    "tr": "tur-Latn",  # Turkish
    "fy": None,  # Western Frisian (not in Epitran list)
    "tl": "tgl-Latn",  # Tagalog
    "as": None,  # Assamese (not in Epitran list)
    "zu": "zul-Latn",  # Zulu
    "bn": "ben-Beng",  # Bengali
    "mns-nor": None,  # Northern Mansi (not in Epitran list)
    "mrw": None,  # Maranao (not in Epitran list)
    "krl": None,  # Karelian (not in Epitran list)
    "ota": None,  # Ottoman Turkish (not in Epitran list)
    "st": None,  # Southern Sotho (not in Epitran list)
    "ru": "rus-Cyrl",  # Russian
    "li": None,  # Limburgish (not in Epitran list)
    "dar": None,  # Dargwa (not in Epitran list)
    "khb": None,  # Lü (not in Epitran list)
    "pl": "pol-Latn",  # Polish
    "wo": None,  # Wolof (not in Epitran list)
    "rup": None,  # Aromanian (not in Epitran list)
    "enf": None,  # Forest Enets (not in Epitran list)
    "roa-leo": None,  # Leonese (not in Epitran list)
    "smi": None,  # Sami (generic, not in Epitran list)
    "or": "ori-Orya",  # Odia
    "alt": None,  # Southern Altai (not in Epitran list)
    "za": "zha-Latn",  # Zhuang
    "cim": None,  # Cimbrian (not in Epitran list)
    "grc": None,  # Ancient Greek (not in Epitran list)
    "th": "tha-Thai",  # Thai
    "hu": "hun-Latn",  # Hungarian
    "kix": None,  # Khiamniungan Naga (not in Epitran list)
    "eu": None,  # Basque (not in Epitran list)
    "vot": None,  # Votic (not in Epitran list)
    "dsb": None,  # Lower Sorbian (not in Epitran list)
    "mnc": None,  # Manchu (not in Epitran list)
    "ig": None,  # Igbo (not in Epitran list)
    "swg": None,  # Swabian German (not in Epitran list)
    "bg": None,  # Bulgarian (not in Epitran list)
    "mt": "mlt-Latn",  # Maltese
    "sm": None,  # Samoan (not in Epitran list)
    "to": None,  # Tongan (not in Epitran list)
    "uz": "uzb-Latn",  # Uzbek (Latin)
    "ilo": "ilo-Latn",  # Ilocano
    "srn": None,  # Sranan Tongo (not in Epitran list)
    "shi": None,  # Tashelhit (not in Epitran list)
    "myv": None,  # Erzya (not in Epitran list)
    "pms": None,  # Piedmontese (not in Epitran list)
    "zza": None,  # Zazaki (not in Epitran list)
    "kab": None,  # Kabyle (not in Epitran list)
    "mdf": None,  # Moksha (not in Epitran list)
    "rmf": None,  # Kalo Finnish Romani (not in Epitran list)
    "inh": None,  # Ingush (not in Epitran list)
    "el": None,  # Modern Greek (not in Epitran list)
    "ase": None,  # American Sign Language (not in Epitran list)
    "ug": "uig-Arab",  # Uyghur
    "sah": None,  # Sakha (not in Epitran list)
    "cv": None,  # Chuvash (not in Epitran list)
    "ff": "ful-Latn",  # Fulah
    "pam": None,  # Kapampangan (not in Epitran list)
    "bo": None,  # Tibetan (not in Epitran list)
    "fi": None,  # Finnish (not in Epitran list)
    "ext": None,  # Extremaduran (not in Epitran list)
    "ka": None,  # Georgian (not in Epitran list)
    "nl": "nld-Latn",  # Dutch
    "ki": None,  # Kikuyu (not in Epitran list)
    "kk": "kaz-Cyrl",  # Kazakh
    "uk": "ukr-Cyrl",  # Ukrainian
    "ab": None,  # Abkhazian (not in Epitran list)
    "ady": None,  # Adyghe (not in Epitran list)
    "id": "ind-Latn",  # Indonesian
    "amu": None,  # Guerrero Amuzgo (not in Epitran list)
    "de": "deu-Latn",  # German
    "frr": None,  # Northern Frisian (not in Epitran list)
    "ht": None,  # Haitian Creole (not in Epitran list)
    "lt": None,  # Lithuanian (not in Epitran list)
    "ja": "jpn-Hrgn",  # Japanese
    "ast": None,  # Asturian (not in Epitran list)
    "abq": None,  # Abaza (not in Epitran list)
    "sgs": None,  # Samogitian (not in Epitran list)
    "bh": None,  # Bihari (not in Epitran list)
    "gld": None,  # Nanai (not in Epitran list)
    "scn": None,  # Sicilian (not in Epitran list)
    "bm": None,  # Bambara (not in Epitran list)
    "cjm": None,  # Eastern Cham (not in Epitran list)
    "so": "som-Latn",  # Somali
    "cho": None,  # Choctaw (not in Epitran list)
    "av": "ava-Cyrl",  # Avaric
    "bua": None,  # Buryat (not in Epitran list)
    "chr": None,  # Cherokee (not in Epitran list)
    "lb": None,  # Luxembourgish (not in Epitran list)
    "vep": None,  # Veps (not in Epitran list)
    "yue": "yue-Latn",  # Cantonese
    "kw": None,  # Cornish (not in Epitran list)
    "evn": None,  # Evenki (not in Epitran list)
    "vec": None,  # Venetian (not in Epitran list)
    "xcl": None,  # Old Armenian (not in Epitran list)
    "haw": None,  # Hawaiian (not in Epitran list)
    "sc": None,  # Sardinian (not in Epitran list)
    "be": None,  # Belarusian (not in Epitran list)
    "rml": None,  # Baltic Romani (not in Epitran list)
    "ia": None,  # Interlingua (not in Epitran list)
    "css": None,  # Southern Ohlone (not in Epitran list)
    "kl": None,  # Kalaallisut (not in Epitran list)
    "aii": "aii-Syrc",  # Assyrian Neo-Aramaic
    "ve": None,  # Venda (not in Epitran list)
    "vro": None,  # Võro (not in Epitran list)
    "km": "khm-Khmr",  # Khmer
    "mer": None,  # Meru (not in Epitran list)
    "br": None,  # Breton (not in Epitran list)
    "oj": None,  # Ojibwe (not in Epitran list)
    "ccp": None,  # Chakma (not in Epitran list)
    "om": "orm-Latn",  # Oromo
    "szl": None,  # Silesian (not in Epitran list)
    "mhr": None,  # Eastern Mari (not in Epitran list)
    "mwl": None,  # Mirandese (not in Epitran list)
    "yi": None,  # Yiddish (not in Epitran list)
    "hrx": None,  # Hunsrik (not in Epitran list)
    "zh": "cmn-Hans",  # Chinese (Simplified)
    "ca": "cat-Latn",  # Catalan
    "an": None,  # Aragonese (not in Epitran list)
    "roa-gal": None,  # Gallo (not in Epitran list)
    "kbd": "kbd-Cyrl",  # Kabardian
    "izh": None,  # Ingrian (not in Epitran list)
    "kum": None,  # Kumyk (not in Epitran list)
    "nn": None,  # Norwegian Nynorsk (not in Epitran list)
    "sel-sou": None,  # Southern Selkup (not in Epitran list)
    "ur": "urd-Arab",  # Urdu
    "hsb": None,  # Upper Sorbian (not in Epitran list)
    "stq": None,  # Saterland Frisian (not in Epitran list)
    "pt": "por-Latn",  # Portuguese
    "cs": "ces-Latn",  # Czech
    "frp": None,  # Franco-Provençal (not in Epitran list)
    "nah": None,  # Nahuatl (not in Epitran list)
    "pdt": None,  # Plautdietsch (not in Epitran list)
    "smj": None,  # Lule Sami (not in Epitran list)
    "gv": None,  # Manx (not in Epitran list)
    "dz": None,  # Dzongkha (not in Epitran list)
    "et": None,  # Estonian (not in Epitran list)
    "jv": "jav-Latn",  # Javanese
    "crs": None,  # Seychellois Creole (not in Epitran list)
    "shy": None,  # Tachawit (not in Epitran list)
    "vo": None,  # Volapük (not in Epitran list)
    "eo": "epo-Latn",  # Esperanto
    "lij": "lij-Latn",  # Ligurian
    "es": "spa-Latn",  # Spanish
    "tyv": None,  # Tuvan (not in Epitran list)
    "xh": "xho-Latn",  # Xhosa
    "cja": None,  # Western Cham (not in Epitran list)
    "sd": None,  # Sindhi (not in Epitran list)
    "ch": None,  # Chamorro (not in Epitran list)
    "hop": None,  # Hopi (not in Epitran list)
    "lv": None,  # Latvian (not in Epitran list)
    "gsw": None,  # Alemannic German (not in Epitran list)
    "ms": "msa-Latn",  # Malay
    "nxq": None,  # Naxi (not in Epitran list)
    "pdc": None,  # Pennsylvania Dutch (not in Epitran list)
    "mk": None,  # Macedonian (not in Epitran list)
    "arc": None,  # Aramaic (not in Epitran list)
    "ckv": None,  # Kavalan (not in Epitran list)
    "crh": None,  # Crimean Tatar (not in Epitran list)
    "io": None,  # Ido (not in Epitran list)
    "wuu": "wuu-Latn",  # Wu Chinese
    "tpi": "tpi-Latn",  # Tok Pisin
    "sn": "sna-Latn",  # Shona
    "fkv": None,  # Kven (not in Epitran list)
    "hil": None,  # Hiligaynon (not in Epitran list)
    "ha": "hau-Latn",  # Hausa
    "sl": None,  # Slovenian (not in Epitran list)
    "iu": None,  # Inuktitut (not in Epitran list)
    "ss": None,  # Swati (not in Epitran list)
    "he": None,  # Hebrew (not in Epitran list)
    "hak": "hak-Latn",  # Hakka
    "fo": None,  # Faroese (not in Epitran list)
    "ko": "kor-Hang",  # Korean
    "rmo": None,  # Sinte Romani (not in Epitran list)
    "sv": "swe-Latn",  # Swedish
    "hy": None,  # Armenian (not in Epitran list)
    "sq": "sqi-Latn",  # Albanian
    "ay": None,  # Aymara (not in Epitran list)
    "ba": None,  # Bashkir (not in Epitran list)
    "la": None,  # Latin (not in Epitran list)
    "os": None,  # Ossetian (not in Epitran list)
    "csb": "csb-Latn",  # Kashubian
    "co": None,  # Corsican (not in Epitran list)
    "sms": None,  # Skolt Sami (not in Epitran list)
    "si": "sin-Sinh",  # Sinhala
    "tet": None,  # Tetum (not in Epitran list)
    "olo": None,  # Livvi-Karelian (not in Epitran list)
    "af": "aar-Latn",  # Afar (using existing mapping)
    "kjh": None,  # Khakas (not in Epitran list)
    "luy": "lsm-Latn",  # Luyia (using Saamia as closest match)
    "ang": None,  # Old English (not in Epitran list)
    "ceb": "ceb-Latn",  # Cebuano
    "rw": "kin-Latn",  # Kinyarwanda
    "qu": "quy-Latn",  # Quechua
    "mg": None,  # Malagasy (not in Epitran list)
    "xal": None,  # Kalmyk (not in Epitran list)
    "lez": None,  # Lezghian (not in Epitran list)
    "cjs": None,  # Shor (not in Epitran list)
    "tcy": None,  # Tulu (not in Epitran list)
    "yo": "yor-Latn",  # Yoruba
    "ckt": None,  # Chukchi (not in Epitran list)
    "lad": None,  # Ladino (not in Epitran list)
    "ar": "ara-Arab",  # Arabic
    "kok": None,  # Konkani (not in Epitran list)
    "fur": None,  # Friulian (not in Epitran list)
    "liv": None,  # Livonian (not in Epitran list)
    "pa": "pan-Guru",  # Punjabi
    "arn": None,  # Mapuche (not in Epitran list)
    "gu": None,  # Gujarati (not in Epitran list)
    "sh": None,  # Serbo-Croatian (not in Epitran list)
    "frm": None,  # Middle French (not in Epitran list)
    "roa-brg": None,  # Bourguignon (not in Epitran list)
    "pap": None,  # Papiamento (not in Epitran list)
    "rmy": None,  # Vlax Romani (not in Epitran list)
    "fr": "fra-Latn",  # French
    "gl": None,  # Galician (not in Epitran list)
    "is": None,  # Icelandic (not in Epitran list)
    "kmr": "kmr-Latn",  # Kurmanji
    "szy": None,  # Sakizaya (not in Epitran list)
    "tk": "tuk-Latn",  # Turkmen
    "wa": None,  # Walloon (not in Epitran list)
    "vi": "vie-Latn",  # Vietnamese
    "nog": None,  # Nogai (not in Epitran list)
    "mnw": None,  # Mon (not in Epitran list)
    "dv": None,  # Dhivehi (not in Epitran list)
    "nb": None,  # Norwegian Bokmål (not in Epitran list)
    "cy": None,  # Welsh (not in Epitran list)
    "hi": "hin-Deva",  # Hindi
    "rmn": None,  # Balkan Romani (not in Epitran list)
    "sco": None,  # Scots (not in Epitran list)
    "sa": None,  # Sanskrit (not in Epitran list)
    "krc": None,  # Karachay-Balkar (not in Epitran list)
    "gd": None,  # Scottish Gaelic (not in Epitran list)
    "kpv": None,  # Komi-Zyrian (not in Epitran list)
    "rmc": None,  # Carpathian Romani (not in Epitran list)
    "ta": "tam-Taml",  # Tamil
    "nds": None,  # Low German (not in Epitran list)
    "ky": "kir-Cyrl",  # Kyrgyz
    "mh": None,  # Marshallese (not in Epitran list)
    "rmw": None,  # Welsh Romani (not in Epitran list)
    "rue": None,  # Rusyn (not in Epitran list)
    "koi": None,  # Komi-Permyak (not in Epitran list)
    "pal": None,  # Middle Persian (not in Epitran list)
    "fa": "fas-Arab",  # Persian/Farsi
    "tt": None,  # Tatar (not in Epitran list)
    "ps": None,  # Pashto (not in Epitran list)
    "ce": None,  # Chechen (not in Epitran list)
    "rm": None,  # Romansh (not in Epitran list)
    "kn": None,  # Kannada (not in Epitran list)
    "mrj": None,  # Western Mari (not in Epitran list)
    "udm": None,  # Udmurt (not in Epitran list)
    "lld": None,  # Ladin (not in Epitran list)
    "rsk": None,  # Pannonian Rusyn (not in Epitran list)
    "new": None,  # Newar (not in Epitran list)
    "mn": "mon-Cyrl-bab",  # Mongolian
    "da": None,  # Danish (not in Epitran list)
    "ltg": None,  # Latgalian (not in Epitran list)
    "abs": None,  # Ambonese Malay (not in Epitran list)
    "ga": None,  # Irish (not in Epitran list)
    "sk": None,  # Slovak (not in Epitran list)
    "nrm": None,  # Norman (not in Epitran list)
    "lbe": None,  # Lak (not in Epitran list)
    "ml": "mal-Mlym",  # Malayalam
    "lo": "lao-Laoo",  # Lao
    "te": "tel-Telu",  # Telugu
    "yrk": None,  # Nenets (not in Epitran list)
    "gag": None,  # Gagauz (not in Epitran list)
    "kaa": None,  # Karakalpak (not in Epitran list)
    "ti": "tir-Ethi",  # Tigrinya
    "gn": None,  # Guarani (not in Epitran list)
}

LANG_TO_EPITRAN = {**OPENSUB_LANGS_TO_EPITRAN, **WIKTIONARY_LANGS_TO_EPITRAN}

ALL_EPITRAN_VALID_LANGUAGES = {k for k, v in LANG_TO_EPITRAN.items() if v is not None}
