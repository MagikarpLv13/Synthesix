"""Guard tests keeping the cockpit redesign fully internationalized.

Generated pages and the home are translated at runtime by ``i18n.js``, which
matches the English source text of each node/attribute against translation
dictionaries. New UI copy that is not added to those dictionaries silently stays
English in every other language. These tests fail fast in that case.
"""

import re
import unittest
from pathlib import Path

from lxml import html

PROJECT_DIR = Path(__file__).resolve().parents[1]

# i18n.js skips these element types when walking the DOM.
SKIPPED_TAGS = {"script", "style", "code", "pre", "datalist", "option"}
TRANSLATED_ATTRIBUTES = ("placeholder", "title", "aria-label")
# Brand, engine names, example placeholders: intentionally language-neutral.
NON_TRANSLATABLE_LITERALS = {
    "Synthesix", "Google", "Bing", "Brave", "DuckDuckGo", "URL",
    "example.com", "cheese", "profile", "admin", "email", "pdf",
}

# UI copy introduced by the cockpit redesign that i18n.js must translate.
# Extend this as new surfaces are migrated.
REDESIGN_STRINGS = [
    "relevant results",
    "strong leads",
    "sources",
    "best score",
    "Sorted by relevance score.",
    "Score 8.0 and above.",
    "Search engines represented.",
    "Highest deterministic relevance.",
    "Found via",
    "navigate results",
    "open",
    "No results matched this search. Adjust the query, filters, "
    "or engines and try again.",
    "No saved searches yet",
    "Run a search from the home page to build your history.",
    "Search scope",
    "Scope",
]


def _dictionary_keys(source, start_marker, end_marker):
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    region = source[start:end]
    return {
        key.replace('\\"', '"')
        for key in re.findall(r'"((?:[^"\\]|\\.)+)"\s*:', region)
    }


def _numeric_patterns(source):
    patterns = []
    for raw in re.findall(r'\[/\^(.+?)\$/,', source):
        try:
            patterns.append(re.compile("^" + raw.replace('\\"', '"') + "$"))
        except re.error:
            continue
    return patterns


class I18nCoverageTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i18n = (PROJECT_DIR / "i18n.js").read_text(encoding="utf-8")
        cls.multilingual = _dictionary_keys(
            cls.i18n, "const multilingual = {", "const languageIndexes"
        )
        cls.additional = _dictionary_keys(
            cls.i18n,
            "const additionalTranslations = {",
            "const additionalLanguageIndexes",
        )
        cls.patterns = _numeric_patterns(cls.i18n)
        cls.home = html.fromstring(
            (PROJECT_DIR / "index.html").read_text(encoding="utf-8")
        )

    def _home_strings(self):
        strings = set()
        for element in self.home.iter():
            tag = element.tag if isinstance(element.tag, str) else ""
            if element.text and tag not in SKIPPED_TAGS:
                value = re.sub(r"\s+", " ", element.text).strip()
                if (
                    len(value) > 1
                    and re.search(r"[A-Za-z]", value)
                    and value not in NON_TRANSLATABLE_LITERALS
                ):
                    strings.add(value)
            for attribute in TRANSLATED_ATTRIBUTES:
                raw = element.get(attribute)
                if not raw:
                    continue
                value = re.sub(r"\s+", " ", raw).strip()
                if (
                    re.search(r"[A-Za-z]", value)
                    and value not in NON_TRANSLATABLE_LITERALS
                ):
                    strings.add(value)
        return strings

    def test_home_ui_strings_are_translated(self):
        """Every visible home string (and translatable attribute) must resolve
        to a translation or numeric pattern in every language."""
        missing = sorted(
            value
            for value in self._home_strings()
            if value not in self.multilingual
            and not any(pattern.match(value) for pattern in self.patterns)
        )
        self.assertEqual(
            missing,
            [],
            "Home strings without translations in i18n.js: "
            + ", ".join(repr(value) for value in missing),
        )

    def test_translation_dictionaries_are_key_synced(self):
        """multilingual (fr/es/zh) and additionalTranslations (pt/de) must hold
        the same keys so no string is translated for only some languages."""
        self.assertEqual(
            self.multilingual - self.additional,
            set(),
            "Keys translated for fr/es/zh but missing pt/de translations.",
        )
        self.assertEqual(
            self.additional - self.multilingual,
            set(),
            "Keys translated for pt/de but missing fr/es/zh translations.",
        )

    def test_redesign_strings_translated_in_all_languages(self):
        missing = sorted(
            value
            for value in REDESIGN_STRINGS
            if value not in self.multilingual or value not in self.additional
        )
        self.assertEqual(
            missing,
            [],
            "Redesign strings without full translations in i18n.js: "
            + ", ".join(repr(value) for value in missing),
        )


if __name__ == "__main__":
    unittest.main()
