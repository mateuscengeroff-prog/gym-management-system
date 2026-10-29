"""Tests for scripts/seed_demo_db.py."""
import io
import os
from contextlib import redirect_stderr, redirect_stdout

from scripts import seed_demo_db as seed
from tests.helpers import TempDatabaseTestCase


class SeedDemoDatabaseTests(TempDatabaseTestCase):
    create_schema = False

    def test_creates_requested_number_of_students(self):
        seed.criarBancoDemo(self.db_path, quantidade=15)
        self.assertEqual(self.query('SELECT COUNT(*) FROM alunos'), [(15,)])

    def test_data_is_fictitious_and_valid(self):
        seed.criarBancoDemo(self.db_path, quantidade=30)
        for nome, idade, sexo, plano, status, data in self.query(
                'SELECT nome, idade, sexo, plano, status, data_matricula FROM alunos'):
            primeiro, sobrenome = nome.split()[:2]
            self.assertIn(primeiro, seed.FIRST_NAMES)
            self.assertIn(sobrenome, seed.LAST_NAMES)
            self.assertTrue(16 <= idade <= 70)
            self.assertIn(sexo, ('masculino', 'feminino'))
            self.assertIn(plano, ('musculacao', 'pilates'))
            self.assertIn(status, ('ativo', 'inativo'))
            self.assertRegex(data, r'^\d{4}-\d{2}-\d{2}$')

    def test_output_is_deterministic(self):
        self.assertEqual(seed.gerarAlunos(10, seed=1), seed.gerarAlunos(10, seed=1))

    def test_refuses_to_overwrite_existing_database(self):
        seed.criarBancoDemo(self.db_path, quantidade=3)
        with self.assertRaises(FileExistsError):
            seed.criarBancoDemo(self.db_path, quantidade=5)
        self.assertEqual(self.query('SELECT COUNT(*) FROM alunos'), [(3,)])

    def test_force_replaces_database(self):
        seed.criarBancoDemo(self.db_path, quantidade=3)
        seed.criarBancoDemo(self.db_path, quantidade=5, force=True)
        self.assertEqual(self.query('SELECT COUNT(*) FROM alunos'), [(5,)])

    def test_command_line_exit_codes(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(seed.main(['--path', self.db_path, '--count', '4']), 0)
            self.assertEqual(seed.main(['--path', self.db_path]), 1)
        self.assertIn('4 fictitious students', out.getvalue())
        self.assertIn('already exists', err.getvalue())
        self.assertTrue(os.path.exists(self.db_path))

    def test_default_path_follows_gym_db_path(self):
        # Regression: the seed used to ignore GYM_DB_PATH while main.py honored it,
        # so reports ran against an empty database after seeding.
        with redirect_stdout(io.StringIO()):
            self.assertEqual(seed.main(['--count', '3']), 0)
        self.assertEqual(self.query('SELECT COUNT(*) FROM alunos'), [(3,)])
