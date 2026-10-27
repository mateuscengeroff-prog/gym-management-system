"""End-to-end tests of the CLI (main.py)."""
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from tests.helpers import TempDatabaseTestCase

import main  # noqa: E402  (imported after helpers sets the headless backend)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FullSessionTest(TempDatabaseTestCase):
    """Drives main() through a whole session with scripted keyboard input."""

    create_schema = False  # main() must create and migrate the database itself

    def run_session(self, inputs):
        with patch('builtins.input', side_effect=list(inputs)), patch.object(main, 'sleep'):
            _, saida = self.quiet(main.main)
        return saida

    def test_crud_and_reports_session(self):
        saida = self.run_session([
            # register two students (with some invalid answers on the way)
            '1', 'Ana Demo', '30', 'f', '2', '1',
            '1', '', 'Bruno Demo', '200', '25', 'm', 'abc', '1', '2',
            '2',                      # list
            '3', 'ANA DEMO',          # search with different case
            '4', '1',                 # report: activity (pie chart)
            '4', '2',                 # report: total
            '4', '3',                 # report: per plan (bar chart)
            '4', '5',                 # report: ages
            '4', '6',                 # report: sex (pie chart)
            '4', '4', '1', 'ana demo', '31',     # edit age
            '4', '4', '2', 'ana demo', '1',      # edit plan -> weight training
            '4', '4', '3', 'bruno demo',         # delete
            '9',                      # unknown option: ignored
            '5',                      # exit
        ])

        self.assertEqual(
            self.query('SELECT nome, idade, sexo, plano, status FROM alunos'),
            [('ana demo', 31, 'feminino', 'musculacao', 'ativo')],
        )
        self.assertIn('Nome: ana demo', saida)
        self.assertIn('Musculacao:1 Pilates:1', saida)
        self.assertIn('Media geral: 27.5 anos', saida)
        self.assertIn('Aluno excluido com sucesso', saida)
        self.assertIn('Encerrando o sistema', saida)

    def test_reports_on_empty_database_do_not_crash(self):
        saida = self.run_session(['4', '1', '4', '3', '4', '5', '4', '6', '5'])
        self.assertIn('Sem dados para gerar o grafico', saida)
        self.assertIn('Media geral: sem dados', saida)


class ScriptEntryPointTests(TempDatabaseTestCase):
    """Runs `python main.py` as a real process."""

    create_schema = False

    def run_script(self, stdin_text):
        env = dict(os.environ, GYM_DB_PATH=self.db_path, MPLBACKEND='Agg')
        return subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, 'main.py')],
            input=stdin_text, capture_output=True, text=True, timeout=30, env=env,
        )

    def test_exit_option(self):
        resultado = self.run_script('5\n')
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn('Encerrando o sistema. Ate logo!', resultado.stdout)
        self.assertTrue(os.path.exists(self.db_path))

    def test_end_of_input_exits_cleanly(self):
        # Regression: closed stdin used to cause an infinite output loop.
        resultado = self.run_script('')
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, '')
        self.assertLess(len(resultado.stdout), 1000)

    def test_runs_from_another_working_directory(self):
        env = dict(os.environ, MPLBACKEND='Agg', GYM_DB_PATH=self.db_path)
        resultado = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, 'main.py')],
            input='5\n', capture_output=True, text=True, timeout=30, env=env,
            cwd=os.path.dirname(self.db_path),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)


if __name__ == '__main__':
    unittest.main()
