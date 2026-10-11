import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "linux" / "auto_cleanup.py"
SPEC = importlib.util.spec_from_file_location("auto_cleanup", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ClassificationTests(unittest.TestCase):
    def test_application_name_is_normalized(self):
        self.assertEqual(MODULE.application_name({"class": "Firefox"}), "firefox")

    def test_initial_class_is_fallback(self):
        self.assertEqual(MODULE.application_name({"initialClass": "Spotify"}), "spotify")

    def test_browser_variants_match(self):
        self.assertTrue(MODULE.matches_any("firefox-nightly", MODULE.BROWSERS))
        self.assertTrue(MODULE.matches_any("com.google-chrome", MODULE.BROWSERS))

    def test_unrelated_substrings_do_not_match(self):
        self.assertFalse(MODULE.matches_any("notspotifyclone", MODULE.NEVER_CLOSE))


if __name__ == "__main__":
    unittest.main()
