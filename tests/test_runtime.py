from __future__ import annotations

import contextlib
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from pytony.runtime import check_path, run_path


class RuntimeTests(unittest.TestCase):
    def test_run_path_imports_pytony_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "saluti.pytony").write_text(
                "strofa saluta(nome):\n"
                "    restero f\"Oh, {schizzo_monet(nome)}\"\n",
                encoding="utf-8",
            )
            (root / "main.pytony").write_text(
                "you_might_also_like saluti\n"
                "spara_minchiate(saluti.saluta('Tony'))\n",
                encoding="utf-8",
            )

            output = StringIO()
            with contextlib.redirect_stdout(output):
                run_path(root / "main.pytony")

            self.assertEqual(output.getvalue(), "Oh, Tony\n")

    def test_check_path_validates_pytony_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "valido.pytony"
            path.write_text(
                "e_se lapalissiano:\n"
                "    spara_minchiate('ciao')\n",
                encoding="utf-8",
            )

            python_source = check_path(path)
            self.assertIn("if True:", python_source)

    def test_check_path_raises_on_invalid_pytony(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rotto.pytony"
            path.write_text(
                "e_se lapalissiano\n"
                "    spara_minchiate('ciao')\n",
                encoding="utf-8",
            )

            with self.assertRaises(SyntaxError):
                check_path(path)
