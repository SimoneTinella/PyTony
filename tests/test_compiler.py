import unittest
import keyword

from pytony.compiler import ALIASES, BUILTIN_ALIASES, KEYWORD_ALIASES, transpile_source


class CompilerTests(unittest.TestCase):
    def test_python_pure_source_is_preserved(self) -> None:
        source = "print('ciao')\nif True:\n    print('ok')\n"
        self.assertEqual(transpile_source(source), source)

    def test_aliases_are_transpiled(self) -> None:
        source = "e_se lapalissiano:\n    spara_minchiate('ciao')\nsenno:\n    spara_minchiate('no')\n"
        expected = "if True:\n    print('ciao')\nelse:\n    print('no')\n"
        self.assertEqual(transpile_source(source), expected)

    def test_mood_aliases_are_transpiled(self) -> None:
        source = "strofa saluta():\n    spara_minchiate('ciao')\nmentre_riposi mica_vero:\n    scoppia RuntimeError('boom')\n"
        expected = "def saluta():\n    print('ciao')\nwhile False:\n    raise RuntimeError('boom')\n"
        self.assertEqual(transpile_source(source), expected)

    def test_alias_values_are_unique(self) -> None:
        self.assertEqual(len(KEYWORD_ALIASES.values()), len(set(KEYWORD_ALIASES.values())))
        self.assertEqual(len(BUILTIN_ALIASES.values()), len(set(BUILTIN_ALIASES.values())))
        self.assertEqual(len(ALIASES.values()), len(set(ALIASES.values())))

    def test_every_python_keyword_has_a_pytony_alias(self) -> None:
        covered = set(KEYWORD_ALIASES.values())
        expected = set(keyword.kwlist) | set(getattr(keyword, "softkwlist", []))
        self.assertTrue(expected.issubset(covered))

    def test_builtins_are_transpiled(self) -> None:
        source = (
            "numeri = popcorn(viaggio_lontano(3))\n"
            "spara_minchiate(fai_la_pesata(numeri))\n"
            "spara_minchiate(lavarei_piatti(numeri))\n"
            "spara_minchiate(schizzo_monet(chi_siamo(numeri)))\n"
        )
        expected = (
            "numeri = list(range(3))\n"
            "print(len(numeri))\n"
            "print(sum(numeri))\n"
            "print(str(type(numeri)))\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_aliases_inside_fstrings_are_transpiled(self) -> None:
        source = 'spara_minchiate(f"Oh, {schizzo_monet(nome)}: {fai_la_pesata(numeri)}")\n'
        expected = 'print(f"Oh, {str(nome)}: {len(numeri)}")\n'
        self.assertEqual(transpile_source(source), expected)

    def test_soft_keywords_are_transpiled(self) -> None:
        source = (
            "interludio numero:\n"
            "    bridge 1:\n"
            "        spara_minchiate('uno')\n"
            "    bridge oh_oh:\n"
            "        spara_minchiate('altro')\n"
        )
        expected = (
            "match numero:\n"
            "    case 1:\n"
                "        print('uno')\n"
            "    case _:\n"
                "        print('altro')\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_strings_and_comments_are_left_untouched(self) -> None:
        source = "# spara_minchiate e fai_la_pesata non vanno toccati\ntext = 'e_se spara_minchiate senno fai_la_pesata'\nspara_minchiate(text)\n"
        expected = "# spara_minchiate e fai_la_pesata non vanno toccati\ntext = 'e_se spara_minchiate senno fai_la_pesata'\nprint(text)\n"
        self.assertEqual(transpile_source(source), expected)


if __name__ == "__main__":
    unittest.main()
