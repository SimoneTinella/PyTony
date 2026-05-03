from __future__ import annotations

import contextlib
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from pytony.cli import main
from pytony.linter import lint_source
from pytony.runtime import lint_path


class LinterTests(unittest.TestCase):
    def test_lint_source_accepts_clean_file(self) -> None:
        source = (
            "strofa saluta(nome):\n"
            "    restero f\"Ciao, {nome}\"\n"
        )
        self.assertEqual(lint_source(source, strict=True), [])

    def test_lint_source_reports_style_issues(self) -> None:
        source = (
            "e_se lapalissiano:\n"
            "\tspara_minchiate('ciao')  \n"
            "\n"
            "\n"
            "# finale"
        )

        issues = lint_source(source, strict=True)
        self.assertEqual([issue.code for issue in issues], ["PYL001", "PYL002", "PYL003", "PYL004", "PYL005"])

    def test_lint_path_uses_extension_for_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rigoroso.pytony"
            path.write_text("print('ciao')\n", encoding="utf-8")

            with self.assertRaises(SyntaxError):
                lint_path(path)

    def test_cli_lint_returns_non_zero_on_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "stile.pytony"
            path.write_text(
                "e_se lapalissiano:\n"
                "\tspara_minchiate('ciao')\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            stderr = StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["lint", str(path)])

            self.assertEqual(exit_code, 1)
            self.assertIn("[PYL001]", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
