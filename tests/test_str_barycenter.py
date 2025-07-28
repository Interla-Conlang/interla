from collections import Counter

import pytest

from assign_spellings_common import IPAProcessor
from str_barycenter import align_words_list, most_common_bary, string_barycenter
from utils import LANG_WEIGHTS


def test_align_words_list_basic():
    words = ["cat", "bat", "rat"]
    aligned = align_words_list(words)
    # Should align to 3 columns, each a tuple of the chars at that position
    assert aligned == [("c", "b", "r"), ("a", "a", "a"), ("t", "t", "t")]


def test_most_common_bary_regular():
    counter = Counter("aab-")
    assert most_common_bary(counter) == "a"


def test_most_common_bary_dash():
    counter = Counter("---a")
    assert most_common_bary(counter) == ""


def test_string_barycenter_weight_length_mismatch():
    with pytest.raises(ValueError):
        string_barycenter(["a", "b"], [1.0])


def test_main_logic_smoke(monkeypatch):
    # Patch logger to avoid logging output during test
    class DummyLogger:
        def debug(self, *a, **kw):
            pass

        def error(self, *a, **kw):
            pass

        def warning(self, *a, **kw):
            pass

        def critical(self, *a, **kw):
            pass

    monkeypatch.setattr("str_barycenter.logger", DummyLogger())

    all_words_with_langs = [
        (
            [
                ("lista", "es"),
                ("Liste", "de"),
                ("list", "en"),
                ("lista", "it"),
                ("cả_thảy", "vi"),
                ("Blacklist", "id"),
                ("Listede", "tr"),
                ("liste", "fr"),
                ("lista", "pt"),
            ],
            [
                "lista",
                "liste",
                "list",
                "lista",
                "kathaj",
                "blatklist",
                "listede",
                "list",
                "liʃta",
            ],
            "lista",
        ),
        (
            [
                ("noir", "fr"),
                ("black", "en"),
                ("schwarz", "de"),
                ("negro", "es"),
                ("nero", "it"),
                ("đen", "vi"),
                ("hitam", "id"),
                ("siyah", "tr"),
                ("preto", "pt"),
            ],
            [
                "nvar",
                "blak",
                "ʃvars",
                "negro",
                "nero",
                "den",
                "hitam",
                "sijah",
                "preto",
            ],
            "nearo",
        ),
        (
            [
                ("Black", "it"),
                ("Sirius", "vi"),
                ("Sirius", "id"),
                ("Sirius", "tr"),
                ("天狼星", "zh_tw"),
                ("Sirius", "pt"),
            ],
            ["blakk", "sizivs", "sirius", "sirius", "thianlaŋiŋ", "sirivʃ"],
            "sirius",
        ),
    ]

    for words_with_langs, processed_words, expected_result in all_words_with_langs:
        weights = [LANG_WEIGHTS[lang] for _, lang in words_with_langs]

        barycenter = string_barycenter(processed_words, weights)
        assert len(barycenter) > 0
        assert isinstance(barycenter, str)
        assert barycenter == expected_result, (
            f"Expected {expected_result} but got {barycenter} for words {words_with_langs}"
        )


if __name__ == "__main__":
    pytest.main([__file__])
