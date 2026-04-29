import unittest
import keyword
from unittest import mock

from pytony.ast_nodes import (
    AsMatchPattern,
    AttributeExpression,
    AssertStatement,
    AugAssignStatement,
    BinaryExpression,
    BreakStatement,
    BoolExpression,
    CallExpression,
    CaptureMatchPattern,
    ClassMatchPattern,
    ClassDefStatement,
    CompareExpression,
    ContinueStatement,
    DictComprehensionExpression,
    ExceptHandler,
    ForStatement,
    FunctionDefStatement,
    GeneratorExpression,
    IfStatement,
    IndexExpression,
    ImportFromStatement,
    ImportStatement,
    LambdaExpression,
    ListComprehensionExpression,
    ListExpression,
    MatchStatement,
    Module,
    NameExpression,
    OrMatchPattern,
    PassStatement,
    RaiseStatement,
    ReturnStatement,
    SequenceMatchPattern,
    SetComprehensionExpression,
    StarMatchPattern,
    SliceExpression,
    StarredExpression,
    DoubleStarredExpression,
    TryStatement,
    ValueMatchPattern,
    WildcardMatchPattern,
    WithStatement,
    WhileStatement,
)
from pytony.compiler import (
    ALIASES,
    BUILTIN_ALIASES,
    KEYWORD_ALIASES,
    PytonySyntaxError,
    transpile_source,
)
from pytony.lowering import lower_module
from pytony.parser import parse_expression, parse_module


class CompilerTests(unittest.TestCase):
    def test_native_expression_parser_builds_call_tree(self) -> None:
        expression = parse_expression("print(len(nome))")
        self.assertIsInstance(expression, CallExpression)
        self.assertIsInstance(expression.function, NameExpression)
        nested = expression.arguments[0]
        self.assertIsInstance(nested, CallExpression)
        self.assertEqual(nested.function.identifier, "len")

    def test_native_expression_parser_builds_keyword_arguments(self) -> None:
        expression = parse_expression("print(nome, end='!')")
        self.assertIsInstance(expression, CallExpression)
        self.assertEqual(len(expression.arguments), 1)
        self.assertEqual(len(expression.keyword_arguments), 1)
        self.assertEqual(expression.keyword_arguments[0].name, "end")

    def test_native_expression_parser_builds_unpacking(self) -> None:
        call_expression = parse_expression("print(*nomi, **opzioni)")
        self.assertIsInstance(call_expression, CallExpression)
        self.assertEqual(len(call_expression.starred_arguments), 1)
        self.assertIsInstance(call_expression.starred_arguments[0], StarredExpression)
        self.assertEqual(len(call_expression.double_starred_arguments), 1)
        self.assertIsInstance(call_expression.double_starred_arguments[0], DoubleStarredExpression)

        list_expression = parse_expression("[*nomi, ultimo]")
        self.assertIsInstance(list_expression, ListExpression)
        self.assertIsInstance(list_expression.elements[0], StarredExpression)

    def test_native_expression_parser_builds_boolean_and_compare_tree(self) -> None:
        expression = parse_expression("nome and contatore < 3")
        self.assertIsInstance(expression, BoolExpression)
        self.assertEqual(expression.operator, "and")
        self.assertIsInstance(expression.values[0], NameExpression)
        self.assertIsInstance(expression.values[1], CompareExpression)

    def test_native_expression_parser_builds_binary_tree(self) -> None:
        expression = parse_expression("contatore + 1")
        self.assertIsInstance(expression, BinaryExpression)
        self.assertEqual(expression.operator, "+")

    def test_native_expression_parser_builds_attribute_and_index_tree(self) -> None:
        expression = parse_expression("rubrica.utenti[0]")
        self.assertIsInstance(expression, IndexExpression)
        self.assertIsInstance(expression.value, AttributeExpression)
        self.assertEqual(expression.value.attribute, "utenti")

    def test_native_expression_parser_builds_slice_tree(self) -> None:
        expression = parse_expression("rubrica.utenti[1:5:2]")
        self.assertIsInstance(expression, SliceExpression)
        self.assertIsInstance(expression.value, AttributeExpression)

    def test_native_expression_parser_builds_list_and_comprehension_tree(self) -> None:
        literal = parse_expression("[nome, contatore]")
        self.assertIsInstance(literal, ListExpression)
        self.assertEqual(len(literal.elements), 2)

        comprehension = parse_expression("[numero for numero in range(5) if numero > 1]")
        self.assertIsInstance(comprehension, ListComprehensionExpression)
        self.assertEqual(comprehension.clauses[0].target, "numero")
        self.assertEqual(len(comprehension.clauses[0].conditions), 1)

    def test_native_expression_parser_builds_generator_and_lambda_tree(self) -> None:
        generator_expression = parse_expression("(numero for numero in range(5) if numero > 1)")
        self.assertIsInstance(generator_expression, GeneratorExpression)
        self.assertEqual(generator_expression.clauses[0].target, "numero")

        lambda_expression = parse_expression("lambda nome: print(nome)")
        self.assertIsInstance(lambda_expression, LambdaExpression)
        self.assertEqual(lambda_expression.parameters, ["nome"])
        self.assertIsInstance(lambda_expression.body, CallExpression)

    def test_native_expression_parser_builds_dict_and_set_comprehensions(self) -> None:
        dict_comprehension = parse_expression("{numero: numero + 1 for numero in range(5)}")
        self.assertIsInstance(dict_comprehension, DictComprehensionExpression)
        self.assertEqual(dict_comprehension.clauses[0].target, "numero")

        set_comprehension = parse_expression("{numero for numero in range(5) if numero > 1}")
        self.assertIsInstance(set_comprehension, SetComprehensionExpression)
        self.assertEqual(len(set_comprehension.clauses[0].conditions), 1)

    def test_first_ast_milestone_parses_supported_subset(self) -> None:
        source = (
            "def saluta(nome):\n"
            "    if nome:\n"
            "        print(nome)\n"
            "    else:\n"
            "        return\n"
        )
        module = parse_module(source)
        self.assertIsInstance(module, Module)
        self.assertEqual(len(module.body), 1)
        function = module.body[0]
        self.assertIsInstance(function, FunctionDefStatement)
        self.assertEqual(function.name, "saluta")
        self.assertEqual(function.parameters[0].name, "nome")
        self.assertIsInstance(function.body[0], IfStatement)
        self.assertIsInstance(function.body[0].orelse[0], ReturnStatement)

    def test_native_statement_parser_does_not_need_ast_parse_for_supported_subset(self) -> None:
        source = (
            "import saluti as ciao\n"
            "from .music import note\n"
            "def canta(nome):\n"
            "    for nota in note:\n"
            "        if nome:\n"
            "            print(nome)\n"
            "    else:\n"
            "        return\n"
        )
        with mock.patch("pytony.parser.ast.parse", side_effect=AssertionError("fallback non ammesso")):
            module = parse_module(source)

        self.assertIsInstance(module, Module)
        self.assertIsInstance(module.body[0], ImportStatement)
        self.assertIsInstance(module.body[1], ImportFromStatement)
        function = module.body[2]
        self.assertIsInstance(function, FunctionDefStatement)
        self.assertEqual(function.name, "canta")
        self.assertIsInstance(function.body[0], ForStatement)
        self.assertIsInstance(function.body[0].body[0], IfStatement)

    def test_native_statement_parser_handles_control_flow_without_ast_parse(self) -> None:
        source = (
            "def scena(nome, stop, errore):\n"
            "    while nome:\n"
            "        if stop:\n"
            "            break\n"
            "        if errore:\n"
            "            raise RuntimeError(nome) from errore\n"
            "        assert nome, 'vuoto'\n"
            "        continue\n"
            "    else:\n"
            "        pass\n"
        )
        with mock.patch("pytony.parser.ast.parse", side_effect=AssertionError("fallback non ammesso")):
            module = parse_module(source)

        function = module.body[0]
        self.assertIsInstance(function, FunctionDefStatement)
        self.assertIsInstance(function.body[0], WhileStatement)
        loop = function.body[0]
        self.assertIsInstance(loop.body[0], IfStatement)
        self.assertIsInstance(loop.body[0].body[0], BreakStatement)
        self.assertIsInstance(loop.body[1], IfStatement)
        self.assertIsInstance(loop.body[1].body[0], RaiseStatement)
        self.assertIsInstance(loop.body[2], AssertStatement)
        self.assertIsInstance(loop.body[3], ContinueStatement)
        self.assertIsInstance(loop.orelse[0], PassStatement)

    def test_native_statement_parser_lowers_control_flow_subset(self) -> None:
        source = (
            "def scena(nome, stop, errore):\n"
            "    while nome:\n"
            "        if stop:\n"
            "            break\n"
            "        if errore:\n"
            "            raise RuntimeError(nome) from errore\n"
            "        assert nome, 'vuoto'\n"
            "        continue\n"
            "    else:\n"
            "        pass\n"
        )
        self.assertEqual(lower_module(parse_module(source)), source)

    def test_native_statement_parser_handles_augassign(self) -> None:
        source = (
            "contatore = 0\n"
            "while contatore < 3:\n"
            "    contatore += 1\n"
        )
        module = parse_module(source)
        loop = module.body[1]
        self.assertIsInstance(loop, WhileStatement)
        self.assertIsInstance(loop.body[0], AugAssignStatement)
        self.assertEqual(lower_module(module), source)

    def test_native_statement_parser_handles_class_with_try_without_ast_parse(self) -> None:
        source = (
            "class Cantante(Base):\n"
            "    pass\n"
            "\n"
            "with open('demo.txt') as handle, lock:\n"
            "    try:\n"
            "        raise RuntimeError('boom')\n"
            "    except RuntimeError as errore:\n"
            "        print(errore)\n"
            "    else:\n"
            "        print('ok')\n"
            "    finally:\n"
            "        handle.close()\n"
        )
        with mock.patch("pytony.parser.ast.parse", side_effect=AssertionError("fallback non ammesso")):
            module = parse_module(source)

        self.assertIsInstance(module.body[0], ClassDefStatement)
        self.assertIsInstance(module.body[1], WithStatement)
        with_statement = module.body[1]
        self.assertEqual(len(with_statement.items), 2)
        self.assertIsInstance(with_statement.body[0], TryStatement)
        try_statement = with_statement.body[0]
        self.assertEqual(len(try_statement.handlers), 1)
        self.assertIsInstance(try_statement.handlers[0], ExceptHandler)

    def test_native_statement_parser_lowers_class_with_try_subset(self) -> None:
        source = (
            "class Cantante(Base):\n"
            "    pass\n"
            "with open('demo.txt') as handle, lock:\n"
            "    try:\n"
            "        raise RuntimeError('boom')\n"
            "    except RuntimeError as errore:\n"
            "        print(errore)\n"
            "    else:\n"
            "        print('ok')\n"
            "    finally:\n"
            "        handle.close()\n"
        )
        self.assertEqual(lower_module(parse_module(source)), source)

    def test_native_statement_parser_handles_match_without_ast_parse(self) -> None:
        source = (
            "match numero:\n"
            "    case 1:\n"
            "        print('uno')\n"
            "    case valore if valore > 1:\n"
            "        print(valore)\n"
            "    case _:\n"
            "        print('altro')\n"
        )
        with mock.patch("pytony.parser.ast.parse", side_effect=AssertionError("fallback non ammesso")):
            module = parse_module(source)

        self.assertIsInstance(module.body[0], MatchStatement)
        match_statement = module.body[0]
        self.assertEqual(len(match_statement.cases), 3)
        self.assertIsNone(match_statement.cases[0].guard)
        self.assertIsNotNone(match_statement.cases[1].guard)
        self.assertEqual(match_statement.cases[2].pattern_source, "_")

    def test_native_statement_parser_builds_pattern_ast_for_common_cases(self) -> None:
        source = (
            "match evento:\n"
            "    case [1, *resto]:\n"
            "        print(resto)\n"
            "    case Colore.ROSSO | 0:\n"
            "        print('rosso')\n"
            "    case Punto(x=1, y=valore) as punto:\n"
            "        print(punto)\n"
            "    case _:\n"
            "        print('altro')\n"
        )
        module = parse_module(source)
        match_statement = module.body[0]
        self.assertIsInstance(match_statement, MatchStatement)

        first_pattern = match_statement.cases[0].pattern
        self.assertIsInstance(first_pattern, SequenceMatchPattern)
        self.assertEqual(first_pattern.kind, "list")
        self.assertIsInstance(first_pattern.elements[1], StarMatchPattern)

        second_pattern = match_statement.cases[1].pattern
        self.assertIsInstance(second_pattern, OrMatchPattern)
        self.assertIsInstance(second_pattern.patterns[0], ValueMatchPattern)

        third_pattern = match_statement.cases[2].pattern
        self.assertIsInstance(third_pattern, AsMatchPattern)
        self.assertIsInstance(third_pattern.pattern, ClassMatchPattern)
        self.assertEqual(third_pattern.name, "punto")
        self.assertIsInstance(third_pattern.pattern.keyword_patterns[1].pattern, CaptureMatchPattern)

        fourth_pattern = match_statement.cases[3].pattern
        self.assertIsInstance(fourth_pattern, WildcardMatchPattern)

    def test_native_statement_parser_lowers_match_subset(self) -> None:
        source = (
            "match numero:\n"
            "    case 1:\n"
            "        print('uno')\n"
            "    case valore if valore > 1:\n"
            "        print(valore)\n"
            "    case _:\n"
            "        print('altro')\n"
        )
        self.assertEqual(lower_module(parse_module(source)), source)

    def test_first_ast_milestone_lowers_back_to_python(self) -> None:
        source = (
            "def saluta(nome):\n"
            "    while nome:\n"
            "        print(nome)\n"
            "        return nome\n"
        )
        self.assertEqual(lower_module(parse_module(source)), source)

    def test_python_pure_source_is_preserved(self) -> None:
        source = "print('ciao')\nif True:\n    print('ok')\n"
        self.assertEqual(transpile_source(source), source)

    def test_strict_mode_rejects_python_keywords_and_builtins(self) -> None:
        source = "if True:\n    print(len([1, 2, 3]))\n"
        with self.assertRaises(PytonySyntaxError) as context:
            transpile_source(source, strict=True)
        self.assertIn("devi scrivere `e_se`", str(context.exception))

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

    def test_list_comprehension_is_transpiled_and_lowered(self) -> None:
        source = (
            "numeri = [numero gira_il_circo numero nell_alta_marea viaggio_lontano(5) e_se numero > 1]\n"
            "spara_minchiate(numeri)\n"
        )
        expected = (
            "numeri = [numero for numero in range(5) if numero > 1]\n"
            "print(numeri)\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_generator_lambda_and_slice_are_transpiled_and_lowered(self) -> None:
        source = (
            "numeri = popcorn(viaggio_lontano(8))\n"
            "finestra = numeri[1:6:2]\n"
            "trasforma = colpo_di_scena numero: numero + 1\n"
            "spara_minchiate(tutti_i_mostri(trasforma(numero) > 1 gira_il_circo numero nell_alta_marea finestra))\n"
        )
        expected = (
            "numeri = list(range(8))\n"
            "finestra = numeri[1:6:2]\n"
            "trasforma = lambda numero: numero + 1\n"
            "print(all((trasforma(numero) > 1 for numero in finestra)))\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_dict_set_comprehensions_and_keyword_arguments_are_transpiled_and_lowered(self) -> None:
        source = (
            "numeri = popcorn(viaggio_lontano(5))\n"
            "mappa = {numero: numero + 1 gira_il_circo numero nell_alta_marea numeri}\n"
            "insieme = {numero gira_il_circo numero nell_alta_marea numeri e_se numero > 1}\n"
            "spara_minchiate(mappa, end='!')\n"
            "spara_minchiate(insieme)\n"
        )
        expected = (
            "numeri = list(range(5))\n"
            "mappa = {numero: numero + 1 for numero in numeri}\n"
            "insieme = {numero for numero in numeri if numero > 1}\n"
            "print(mappa, end='!')\n"
            "print(insieme)\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_ritornello_is_transpiled_as_a_counted_loop(self) -> None:
        source = (
            "ritornello 3:\n"
            "    spara_minchiate('ancora')\n"
        )
        expected = (
            "for __pytony_ritornello_1 in range(3):\n"
            "    print('ancora')\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_duetto_is_transpiled_as_a_zip_loop(self) -> None:
        source = (
            "duetto nome, coro con nomi, cori:\n"
            "    spara_minchiate(nome, coro)\n"
        )
        expected = (
            "for nome, coro in zip(nomi, cori):\n"
            "    print(nome, coro)\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_ancora_una_volta_is_transpiled_as_a_do_while_loop(self) -> None:
        source = (
            "contatore = 0\n"
            "ancora_una_volta contatore < 3:\n"
            "    spara_minchiate(contatore)\n"
            "    contatore += 1\n"
        )
        expected = (
            "contatore = 0\n"
            "while True:\n"
            "    print(contatore)\n"
            "    contatore += 1\n"
            "    if not (contatore < 3):\n"
            "        break\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_unpacking_is_transpiled_and_lowered(self) -> None:
        source = (
            "nomi = ['Tony']\n"
            "altri = ['Pitony']\n"
            "fratelli = [*nomi, *altri, 'Live']\n"
            "rubrica = {'nome': 'Tony', **{'cognome': 'Pitony'}}\n"
            "opzioni = {'end': '!'}\n"
            "spara_minchiate(*fratelli, **opzioni)\n"
        )
        expected = (
            "nomi = ['Tony']\n"
            "altri = ['Pitony']\n"
            "fratelli = [*nomi, *altri, 'Live']\n"
            "rubrica = {'nome': 'Tony', **{'cognome': 'Pitony'}}\n"
            "opzioni = {'end': '!'}\n"
            "print(*fratelli, **opzioni)\n"
        )
        self.assertEqual(transpile_source(source), expected)

    def test_strict_mode_reports_pytony_syntax_errors(self) -> None:
        source = "e_se lapalissiano\n    spara_minchiate('ciao')\n"
        with self.assertRaises(PytonySyntaxError) as context:
            transpile_source(source, strict=True)
        self.assertIn("Sintassi Pytony non valida", str(context.exception))

    def test_strict_mode_prefers_native_match_diagnostics(self) -> None:
        source = (
            "interludio numero:\n"
            "    spara_minchiate('senza bridge')\n"
        )
        with self.assertRaises(PytonySyntaxError) as context:
            transpile_source(source, strict=True)

        message = str(context.exception)
        self.assertIn("Dentro `match` ogni blocco deve iniziare con `case`", message)
        self.assertIn("(riga 2, colonna 5)", message)
        self.assertIn("^", message)

    def test_aliases_inside_fstrings_are_transpiled(self) -> None:
        source = 'spara_minchiate(f"Oh, {schizzo_monet(nome)}: {fai_la_pesata(numeri)}")\n'
        expected = 'print(f"Oh, {str(nome)}: {len(numeri)}")\n'
        self.assertEqual(transpile_source(source), expected)

    def test_strict_mode_rejects_python_inside_fstrings(self) -> None:
        source = 'spara_minchiate(f"Oh, {str(nome)}: {len(numeri)}")\n'
        with self.assertRaises(PytonySyntaxError) as context:
            transpile_source(source, strict=True)
        self.assertIn("devi scrivere `schizzo_monet`", str(context.exception))

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

    def test_exclusive_constructs_do_not_rewrite_multiline_strings(self) -> None:
        source = (
            "manifesto = '''\n"
            "ritornello 3:\n"
            "    duetto nome, coro con nomi, cori:\n"
            "ancora_una_volta lapalissiano:\n"
            "'''\n"
            "spara_minchiate(manifesto)\n"
        )
        expected = (
            "manifesto = '''\n"
            "ritornello 3:\n"
            "    duetto nome, coro con nomi, cori:\n"
            "ancora_una_volta lapalissiano:\n"
            "'''\n"
            "print(manifesto)\n"
        )
        self.assertEqual(transpile_source(source), expected)


if __name__ == "__main__":
    unittest.main()
