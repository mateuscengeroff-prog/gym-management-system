"""Create a local SQLite database filled with FICTITIOUS demo students.

Usage (from the project root):

    python scripts/seed_demo_db.py                 # creates academia.db
    python scripts/seed_demo_db.py --path demo.db  # custom location
    python scripts/seed_demo_db.py --count 40 --force

Safety rules:
- Every name is generated from the invented lists below; no real data is used.
- An existing database is never overwritten unless --force is given, so a
  database with real records cannot be destroyed by accident.
- The output is deterministic (fixed random seed), so demos and screenshots
  are reproducible.
"""
import argparse
import os
import random
import sys
from datetime import date, timedelta

# Allow "python scripts/seed_demo_db.py" to import the project's lib package.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FIRST_NAMES = [
    'ana', 'bruno', 'carla', 'diego', 'elisa', 'fabio', 'gabriela', 'heitor',
    'isadora', 'joao', 'karina', 'lucas', 'marina', 'nicolas', 'olivia',
    'paulo', 'renata', 'samuel', 'tatiana', 'vitor',
]
LAST_NAMES = ['demo', 'exemplo', 'teste', 'ficticio']
SEXES = {
    'ana': 'feminino', 'carla': 'feminino', 'elisa': 'feminino',
    'gabriela': 'feminino', 'isadora': 'feminino', 'karina': 'feminino',
    'marina': 'feminino', 'olivia': 'feminino', 'renata': 'feminino',
    'tatiana': 'feminino',
}


def gerarAlunos(quantidade, seed=42, hoje=None):
    """Return a list of fictitious student tuples (nome, idade, sexo, plano, status, data)."""
    rng = random.Random(seed)
    hoje = hoje or date.today()
    alunos = []
    for i in range(quantidade):
        primeiro = FIRST_NAMES[i % len(FIRST_NAMES)]
        sobrenome = LAST_NAMES[(i // len(FIRST_NAMES)) % len(LAST_NAMES)]
        nome = f'{primeiro} {sobrenome}'
        if i >= len(FIRST_NAMES) * len(LAST_NAMES):
            nome = f'{nome} {i}'  # keep names unique for large counts
        sexo = SEXES.get(primeiro, 'masculino')
        idade = rng.randint(16, 70)
        plano = rng.choice(['musculacao', 'musculacao', 'pilates'])
        status = 'ativo' if rng.random() < 0.75 else 'inativo'
        data = hoje - timedelta(days=rng.randint(0, 730))
        alunos.append((nome, idade, sexo, plano, status, data))
    return alunos


def criarBancoDemo(caminho, quantidade=20, force=False, seed=42):
    """Create the demo database at `caminho`. Returns the number of students inserted."""
    if os.path.exists(caminho):
        if not force:
            raise FileExistsError(
                f'{caminho} already exists. Use --force to replace it '
                '(this deletes every record in that file).'
            )
        os.remove(caminho)

    os.environ['GYM_DB_PATH'] = os.path.abspath(caminho)
    from lib import banco_de_dados as db

    db.criarBanco()
    db.atualizarBanco()
    conexao = db.conectar()
    conexao.executemany("""
    INSERT INTO alunos(nome, idade, sexo, plano, status, data_matricula)
    VALUES(?, ?, ?, ?, ?, ?)
""", [(n, i, s, p, st, d.isoformat()) for n, i, s, p, st, d in gerarAlunos(quantidade, seed)])
    conexao.commit()
    conexao.close()
    return quantidade


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create a SQLite database with fictitious demo students.')
    parser.add_argument('--path', default=os.path.join(PROJECT_ROOT, 'academia.db'),
                        help='database file to create (default: academia.db in the project root)')
    parser.add_argument('--count', type=int, default=20, help='number of students (default: 20)')
    parser.add_argument('--seed', type=int, default=42, help='random seed (default: 42)')
    parser.add_argument('--force', action='store_true', help='replace the file if it already exists')
    args = parser.parse_args(argv)

    if args.count < 1:
        parser.error('--count must be at least 1')

    try:
        total = criarBancoDemo(args.path, args.count, args.force, args.seed)
    except FileExistsError as erro:
        print(f'Error: {erro}', file=sys.stderr)
        return 1

    print(f'Created {args.path} with {total} fictitious students.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
