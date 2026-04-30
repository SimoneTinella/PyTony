from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pytony.formatter import format_source
from pytony.runtime import format_path


class FormatterTests(unittest.TestCase):
    def test_format_source_normalizes_indentation_spacing_and_comments(self) -> None:
        source = (
            "e_se lapalissiano:\n"
            "\t spara_minchiate('ciao',end='!')  # nota\n"
            "\n"
            "ritornello  3 :\n"
            "  spara_minchiate( *nomi,**opzioni)\n"
        )
        expected = (
            "e_se lapalissiano:\n"
            "    spara_minchiate('ciao', end='!')  # nota\n"
            "\n"
            "ritornello 3:\n"
            "    spara_minchiate(*nomi, **opzioni)\n"
        )
        self.assertEqual(format_source(source), expected)

    def test_format_source_preserves_comment_only_lines(self) -> None:
        source = (
            "# apertura\n"
            "strofa saluta(nome):\n"
            "    # dentro\n"
            "    restero nome\n"
        )
        self.assertEqual(format_source(source), source)

    def test_format_path_reports_and_writes_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "demo.pytony"
            path.write_text(
                "duetto nome,coro con nomi,cori:\n"
                "\tspara_minchiate(nome,coro)\n",
                encoding="utf-8",
            )

            preview, changed = format_path(path)
            self.assertTrue(changed)
            self.assertIn("duetto nome, coro con nomi, cori:", preview)

            written, changed_after_write = format_path(path, write=True)
            self.assertTrue(changed_after_write)
            self.assertEqual(path.read_text(encoding="utf-8"), written)

            _, changed_after_second_pass = format_path(path)
            self.assertFalse(changed_after_second_pass)


if __name__ == "__main__":
    unittest.main()
