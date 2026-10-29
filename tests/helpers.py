"""Shared test helpers: every test runs against its own temporary database."""
import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout

# Headless Matplotlib backend so charts never open a window during tests.
os.environ.setdefault('MPLBACKEND', 'Agg')

from lib import banco_de_dados as db  # noqa: E402


class TempDatabaseTestCase(unittest.TestCase):
    """Points GYM_DB_PATH to a fresh temporary SQLite file for each test."""

    create_schema = True

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self._tmpdir.name, 'test.db')
        self._old_env = os.environ.get('GYM_DB_PATH')
        os.environ['GYM_DB_PATH'] = self.db_path
        if self.create_schema:
            db.criarBanco()
            db.atualizarBanco()

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop('GYM_DB_PATH', None)
        else:
            os.environ['GYM_DB_PATH'] = self._old_env
        self._tmpdir.cleanup()

    def quiet(self, func, *args, **kwargs):
        """Call func while capturing its printed output. Returns (result, output)."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = func(*args, **kwargs)
        return result, buffer.getvalue()

    def query(self, sql, params=()):
        conexao = sqlite3.connect(self.db_path)
        try:
            return conexao.execute(sql, params).fetchall()
        finally:
            conexao.close()

    def add(self, nome='ana demo', idade=30, sexo='feminino', plano='musculacao', status='ativo', **kwargs):
        novo_id, _ = self.quiet(db.cadastrarBanco, nome, idade, sexo, plano, status, **kwargs)
        return novo_id
