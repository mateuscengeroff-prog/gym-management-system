"""Tests for the SQLite data layer (lib/banco_de_dados)."""
import os
import sqlite3
from datetime import date

from lib import banco_de_dados as db
from tests.helpers import TempDatabaseTestCase


class SchemaAndMigrationTests(TempDatabaseTestCase):
    create_schema = False

    def columns(self):
        return [row[1] for row in self.query('PRAGMA table_info(alunos)')]

    def test_fresh_database_gets_full_schema(self):
        db.criarBanco()
        db.atualizarBanco()
        self.assertEqual(
            self.columns(),
            ['id', 'nome', 'idade', 'sexo', 'plano', 'status', 'data_matricula'],
        )

    def test_migration_is_idempotent(self):
        db.criarBanco()
        db.atualizarBanco()
        db.atualizarBanco()  # second run must not fail (no duplicate column)
        self.assertEqual(self.columns().count('data_matricula'), 1)

    def test_migration_upgrades_legacy_database_and_keeps_rows(self):
        # Schema used by the first version of the project (no data_matricula).
        conexao = sqlite3.connect(self.db_path)
        conexao.execute(
            'CREATE TABLE alunos(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, '
            'idade INTEGER, sexo TEXT, plano TEXT, status TEXT)'
        )
        conexao.execute(
            "INSERT INTO alunos(nome, idade, sexo, plano, status) "
            "VALUES('ana demo', 30, 'feminino', 'pilates', 'ativo')"
        )
        conexao.commit()
        conexao.close()

        db.criarBanco()  # CREATE TABLE IF NOT EXISTS must not touch it
        db.atualizarBanco()

        self.assertIn('data_matricula', self.columns())
        self.assertEqual(self.query('SELECT nome, data_matricula FROM alunos'), [('ana demo', None)])

    def test_migration_fixes_misspelled_plan_from_old_version(self):
        db.criarBanco()
        db.atualizarBanco()
        conexao = sqlite3.connect(self.db_path)
        conexao.execute("INSERT INTO alunos(nome, plano) VALUES('bruno demo', 'musulacao')")
        conexao.commit()
        conexao.close()

        db.atualizarBanco()

        self.assertEqual(self.query('SELECT plano FROM alunos'), [('musculacao',)])

    def test_default_path_is_project_root_not_current_directory(self):
        os.environ.pop('GYM_DB_PATH')
        caminho = db.caminhoBanco()
        os.environ['GYM_DB_PATH'] = self.db_path  # restore for tearDown
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(caminho, os.path.join(raiz, 'academia.db'))


class CreateReadTests(TempDatabaseTestCase):

    def test_register_normalizes_and_stores_iso_date(self):
        novo_id = self.add(nome='  Ana DEMO ', sexo='Feminino', plano='Pilates', status='Ativo')
        rows = self.query('SELECT id, nome, idade, sexo, plano, status, data_matricula FROM alunos')
        self.assertEqual(rows, [(novo_id, 'ana demo', 30, 'feminino', 'pilates', 'ativo', date.today().isoformat())])

    def test_register_accepts_explicit_enrollment_date(self):
        self.add(data_matricula=date(2025, 1, 15))
        self.assertEqual(self.query('SELECT data_matricula FROM alunos'), [('2025-01-15',)])

    def test_list_returns_every_student(self):
        self.add(nome='ana demo')
        self.add(nome='bruno demo')
        alunos, saida = self.quiet(db.listarAlunosBanco)
        self.assertEqual([a[1] for a in alunos], ['ana demo', 'bruno demo'])
        self.assertIn('Nome: bruno demo', saida)

    def test_list_on_empty_database(self):
        alunos, saida = self.quiet(db.listarAlunosBanco)
        self.assertEqual(alunos, [])
        self.assertIn('Nenhum aluno cadastrado', saida)

    def test_search_ignores_case_and_surrounding_spaces(self):
        self.add(nome='Ana Demo')
        alunos, _ = self.quiet(db.buscarAlunoBanco, '  ANA demo ')
        self.assertEqual(len(alunos), 1)

    def test_search_not_found(self):
        alunos, saida = self.quiet(db.buscarAlunoBanco, 'ninguem')
        self.assertEqual(alunos, [])
        self.assertIn('Aluno nao encontrado', saida)

    def test_search_returns_all_students_with_same_name(self):
        self.add(nome='ana demo', idade=20)
        self.add(nome='ana demo', idade=40)
        alunos, _ = self.quiet(db.buscarAlunoBanco, 'ana demo')
        self.assertEqual(sorted(a[2] for a in alunos), [20, 40])

    def test_queries_are_parameterized(self):
        nome_malicioso = "x'; DROP TABLE alunos; --"
        self.add(nome=nome_malicioso)
        alunos, _ = self.quiet(db.buscarAlunoBanco, nome_malicioso)
        self.assertEqual(len(alunos), 1)
        self.assertEqual(self.quiet(db.contarAlunosBanco)[0], 1)


class UpdateDeleteTests(TempDatabaseTestCase):

    def test_edit_age(self):
        self.add(nome='ana demo', idade=30)
        alterados, _ = self.quiet(db.editarIdadeBanco, 'ANA DEMO', 31)
        self.assertEqual(alterados, 1)
        self.assertEqual(self.query('SELECT idade FROM alunos'), [(31,)])

    def test_edit_age_not_found(self):
        alterados, saida = self.quiet(db.editarIdadeBanco, 'ninguem', 31)
        self.assertEqual(alterados, 0)
        self.assertIn('Aluno nao encontrado', saida)

    def test_edit_plan_to_weight_training_uses_correct_spelling(self):
        # Regression: the old code stored 'musulacao', hiding the student from reports.
        self.add(nome='ana demo', plano='pilates')
        self.quiet(db.editarPlanoBanco, 'ana demo', 1)
        self.assertEqual(self.query('SELECT plano FROM alunos'), [('musculacao',)])
        (m, p), _ = self.quiet(db.alunosPorPlanoBanco)
        self.assertEqual((m, p), (1, 0))

    def test_edit_plan_to_pilates(self):
        self.add(nome='ana demo', plano='musculacao')
        alterados, _ = self.quiet(db.editarPlanoBanco, 'ana demo', 2)
        self.assertEqual(alterados, 1)
        self.assertEqual(self.query('SELECT plano FROM alunos'), [('pilates',)])

    def test_edit_plan_not_found(self):
        alterados, _ = self.quiet(db.editarPlanoBanco, 'ninguem', 2)
        self.assertEqual(alterados, 0)

    def test_delete(self):
        self.add(nome='ana demo')
        self.add(nome='bruno demo')
        excluidos, saida = self.quiet(db.excluirAlunoBanco, 'Ana Demo')
        self.assertEqual(excluidos, 1)
        self.assertIn('excluido com sucesso', saida)
        self.assertEqual(self.query('SELECT nome FROM alunos'), [('bruno demo',)])

    def test_delete_not_found(self):
        excluidos, saida = self.quiet(db.excluirAlunoBanco, 'ninguem')
        self.assertEqual(excluidos, 0)
        self.assertIn('Aluno nao encontrado', saida)


class ReportTests(TempDatabaseTestCase):

    def setUp(self):
        super().setUp()
        self.add(nome='ana demo', idade=20, sexo='feminino', plano='musculacao', status='ativo')
        self.add(nome='bruno demo', idade=30, sexo='masculino', plano='musculacao', status='inativo')
        self.add(nome='carla demo', idade=40, sexo='feminino', plano='pilates', status='ativo')

    def test_count(self):
        self.assertEqual(db.contarAlunosBanco(), 3)

    def test_activity(self):
        resultado, _ = self.quiet(db.atividadesAlunos)
        self.assertEqual(resultado, (2, 1))

    def test_students_per_plan(self):
        resultado, saida = self.quiet(db.alunosPorPlanoBanco)
        self.assertEqual(resultado, (2, 1))
        self.assertIn('Musculacao:2 Pilates:1', saida)

    def test_age_averages(self):
        (geral, musculacao, pilates), saida = self.quiet(db.mediaIdadesBanco)
        self.assertAlmostEqual(geral, 30.0)
        self.assertAlmostEqual(musculacao, 25.0)
        self.assertAlmostEqual(pilates, 40.0)
        self.assertIn('Media geral: 30.0 anos', saida)
        self.assertNotIn('(', saida)  # old version printed raw tuples like (30.0,)

    def test_sex_statistics(self):
        resultado, saida = self.quiet(db.porSexoBanco)
        self.assertEqual(resultado, (1, 2))
        self.assertIn('Mulheres: 2 (66.7%)', saida)


class EmptyDatabaseReportTests(TempDatabaseTestCase):

    def test_reports_do_not_crash_on_empty_database(self):
        self.assertEqual(db.contarAlunosBanco(), 0)
        self.assertEqual(self.quiet(db.atividadesAlunos)[0], (0, 0))
        self.assertEqual(self.quiet(db.alunosPorPlanoBanco)[0], (0, 0))

    def test_age_averages_empty(self):
        resultado, saida = self.quiet(db.mediaIdadesBanco)
        self.assertEqual(resultado, (None, None, None))
        self.assertIn('Media geral: sem dados', saida)

    def test_sex_statistics_empty_returns_zeros(self):
        # Regression: used to return None, crashing `h, m = porSexoBanco()`.
        resultado, _ = self.quiet(db.porSexoBanco)
        self.assertEqual(resultado, (0, 0))
