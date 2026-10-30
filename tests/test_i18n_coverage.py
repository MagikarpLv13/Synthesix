"""The browser UI and backend statuses must remain translated in all languages."""
import ast
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class I18nCoverageTestCase(unittest.TestCase):
    def test_browser_copy_and_validation_errors_have_all_five_translations(self):
        source = (ROOT / "i18n.js").read_text(encoding="utf-8")
        def keys(start, end):
            part = source[source.index(start):source.index(end, source.index(start))]
            return {json.loads('"' + key + '"') for key in re.findall(r'"((?:[^"\\]|\\.)+)"\s*:', part)}
        multi = keys("const multilingual = {", "const languageIndexes")
        additional = keys("const additionalTranslations = {", "const additionalLanguageIndexes")
        component = (ROOT / "frontend/src/components/sx-browser-app.ts").read_text(encoding="utf-8")
        literals = set(re.findall(r'\bthis\.t\("([^"\n]+)"\)', component))
        literals.update(["Site", "Exclude", "File type", "Title contains", "URL contains", "Page contains", "Country code", "After", "Before", "Queries", "Search", "Browser profiles", "History", "One query per line", "No results match this filter.", "Searching selected engines...", "Your next search starts here.", "Starting Synthesix...", "Application disconnected. Launch Synthesix to use this page."])
        for filename in ["storage.py", "profiles.py", "search.py", "runtime.py"]:
            tree = ast.parse((ROOT / "app" / filename).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) and node.exc.func.id == "ValueError":
                    literals.update(n.value for n in node.exc.args if isinstance(n, ast.Constant) and isinstance(n.value, str))
                if isinstance(node, ast.keyword) and node.arg == "status":
                    literals.update(n.value for n in ast.walk(node.value) if isinstance(n, ast.Constant) and isinstance(n.value, str))
        literals.discard("Unsupported browser database version.")  # Startup error, never UI copy.
        self.assertEqual(sorted(literals - multi), [])
        self.assertEqual(sorted(literals - additional), [])

    def test_exported_translator_uses_browser_dictionary_in_every_language(self):
        script = r"""const fs=require('fs'),vm=require('vm');
const context={window:{},document:{readyState:'loading',addEventListener(){}}};
vm.createContext(context);vm.runInContext(fs.readFileSync('i18n.js','utf8'),context);
const t=context.window.synthesixI18n.t;
console.log(JSON.stringify(['fr','es','zh','pt','de'].map(lang=>t('Browser profiles',lang))));"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
        translations = json.loads(result.stdout)
        self.assertEqual(len(translations), 5)
        self.assertTrue(all(t and t != "Browser profiles" for t in translations))
