"""Tests for the terminal input helpers (lib/inter)."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from lib import inter


def run_with_inputs(func, inputs, *args):
    """Run func feeding `inputs` to input(); returns (result, printed output)."""
    buffer = io.StringIO()
    with patch('builtins.input', side_effect=list(inputs)), redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


class LeiaIntTests(unittest.TestCase):

    def test_returns_integer(self):
        self.assertEqual(run_with_inputs(inter.leiaInt, ['42'], '> ')[0], 42)

    def test_retries_until_valid(self):
        resultado, saida = run_with_inputs(inter.leiaInt, ['abc', '', '3.5', '7'], '> ')
        self.assertEqual(resultado, 7)
        self.assertEqual(saida.count('Digite um valor valido'), 3)

    def test_end_of_input_is_not_swallowed(self):
        # Regression: a bare `except:` caught EOFError and looped forever.
        with self.assertRaises(EOFError):
            run_with_inputs(inter.leiaInt, [EOFError()], '> ')


class ChoiceReaderTests(unittest.TestCase):

    def test_plan(self):
        self.assertEqual(run_with_inputs(inter.leiaPlano, ['1'], '> ')[0], 'musculacao')
        self.assertEqual(run_with_inputs(inter.leiaPlano, ['2'], '> ')[0], 'pilates')

    def test_plan_rejects_invalid_and_non_numeric(self):
        # Regression: non-numeric input used to raise ValueError and crash.
        resultado, saida = run_with_inputs(inter.leiaPlano, ['abc', '9', '2'], '> ')
        self.assertEqual(resultado, 'pilates')
        self.assertEqual(saida.count('Digite um valor valido'), 2)

    def test_status(self):
        self.assertEqual(run_with_inputs(inter.leiaStatus, ['1'], '> ')[0], 'ativo')
        self.assertEqual(run_with_inputs(inter.leiaStatus, ['x', '0', '2'], '> ')[0], 'inativo')

    def test_sex_accepts_case_and_spaces(self):
        self.assertEqual(run_with_inputs(inter.leiaSexo, [' M '], '> ')[0], 'masculino')
        self.assertEqual(run_with_inputs(inter.leiaSexo, ['x', 'f'], '> ')[0], 'feminino')

    def test_name_rejects_blank(self):
        resultado, saida = run_with_inputs(inter.leiaNome, ['', '   ', ' Ana Demo '], '> ')
        self.assertEqual(resultado, 'Ana Demo')
        self.assertEqual(saida.count('nao pode ficar em branco'), 2)

    def test_age_range(self):
        resultado, saida = run_with_inputs(inter.leiaIdade, ['-1', '0', '121', 'abc', '35'], '> ')
        self.assertEqual(resultado, 35)
        self.assertEqual(saida.count('Digite uma idade entre 1 e 120'), 3)

    def test_menu_prints_numbered_options(self):
        resultado, saida = run_with_inputs(inter.menu, ['2'], ['Um', 'Dois'])
        self.assertEqual(resultado, 2)
        self.assertIn('1 - Um', saida)
        self.assertIn('2 - Dois', saida)


class FormattingTests(unittest.TestCase):

    def test_line(self):
        self.assertEqual(inter.linha(), '-' * 42)
        self.assertEqual(inter.linha(5), '-----')
