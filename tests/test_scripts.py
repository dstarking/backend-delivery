"""Run from skill root: python -m unittest discover -s tests -v"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from init_project import initialize, checked_id
from validate_docs import inspect


class InitAndValidationTests(unittest.TestCase):
    def test_create_and_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = initialize(repo, "demo", "core-module")
            self.assertTrue((folder / "02-technical-design.md").is_file())
            self.assertTrue((folder / "03-modules/core-module-plan.md").is_file())
            self.assertTrue((folder / "04-module-tests/core-module-test.md").is_file())
            errors, warnings = inspect(repo, "demo")
            self.assertEqual(errors, [])

    def test_idempotent_never_overwrites_user_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = initialize(repo, "demo", "module-a")
            doc = folder / "01-requirements.md"
            doc.write_text("# 实际人工需求\n", encoding="utf-8")
            initialize(repo, "demo", "module-a")
            self.assertEqual(doc.read_text(encoding="utf-8"), "# 实际人工需求\n")

    def test_bad_id_rejected(self):
        for project in ("../oops", "A_B", "-abc", "abc-", "a/b", ""):
            with self.assertRaises(ValueError):
                checked_id(project, "project")

    def test_missing_critical_file_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = initialize(repo, "demo")
            (folder / "02-technical-design.md").unlink()
            errors, _ = inspect(repo, "demo")
            self.assertTrue(any("02-technical-design" in err for err in errors))

    def test_design_phase_rejects_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            initialize(repo, "demo")
            errors, _ = inspect(repo, "demo", "design")
            self.assertTrue(any("占位" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
