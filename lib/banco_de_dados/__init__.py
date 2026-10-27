"""Camada de acesso ao banco SQLite da academia.

Cada funcao abre a conexao, executa a operacao e fecha a conexao.
As funcoes imprimem o resultado para o usuario (CLI) e tambem retornam
os dados, o que permite testa-las automaticamente.
"""
import os
import sqlite3
from datetime import date

from lib.inter import cabecalho, linha

# Pasta raiz do projeto (dois niveis acima deste arquivo: lib/banco_de_dados/)
PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def caminhoBanco():
    """Caminho do arquivo do banco.

    Usa a variavel de ambiente GYM_DB_PATH se existir; senao, academia.db na
    raiz do projeto. Antes o caminho era relativo ao diretorio atual, entao
    rodar o programa de outra pasta criava um banco novo e vazio.
    """
    return os.environ.get('GYM_DB_PATH', os.path.join(PASTA_PROJETO, 'academia.db'))


def conectar():
    return sqlite3.connect(caminhoBanco())


def normalizarNome(nome):
    """Nomes sao guardados em minusculas e sem espacos nas pontas."""
    return str(nome).strip().lower()


def imprimirAluno(aluno):
    print(f'ID: {aluno[0]}')
    print(f'Nome: {aluno[1]}')
    print(f'Idade: {aluno[2]}')
    print(f'Sexo: {aluno[3]}')
    print(f'Plano: {aluno[4]}')
    print(f'Status: {aluno[5]}')
    print(f'Data de matricula: {aluno[6]}')
    print(linha())


def criarBanco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT,
                   idade INTEGER,
                   sexo TEXT,
                   plano TEXT,
                   status TEXT)
""")
    conexao.commit()
    conexao.close()


def atualizarBanco():
    """Migracoes do banco. Podem ser executadas varias vezes sem efeito colateral.

    1. Adiciona a coluna data_matricula em bancos criados antes dela existir.
    2. Corrige registros gravados com o plano 'musulacao' (erro de digitacao
       da versao anterior de editarPlanoBanco).
    """
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('PRAGMA table_info(alunos)')

    colunas = cursor.fetchall()
    existe = False

    for coluna in colunas:
        if coluna[1] == 'data_matricula':
            existe = True

    if not existe:
        cursor.execute("""
        ALTER TABLE alunos
        ADD COLUMN data_matricula TEXT
        """)

    cursor.execute("""
    UPDATE alunos
    SET plano = 'musculacao'
    WHERE plano = 'musulacao'
""")

    conexao.commit()
    conexao.close()


def cadastrarBanco(nome, idade, sexo, plano, status, data_matricula=None):
    """Cadastra um aluno e retorna o id gerado.

    A data e gravada como texto ISO (AAAA-MM-DD): o adaptador automatico de
    date do sqlite3 esta obsoleto desde o Python 3.12.
    """
    if data_matricula is None:
        data_matricula = date.today()

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    INSERT INTO alunos(nome, idade, sexo, plano, status, data_matricula)
    VALUES(?, ?, ?, ?, ?, ?)
""", (normalizarNome(nome), idade, sexo.lower(), plano.lower(), status.lower(), data_matricula.isoformat()))

    novo_id = cursor.lastrowid
    conexao.commit()
    conexao.close()

    print('Aluno cadastrado com sucesso')
    return novo_id


def listarAlunosBanco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM alunos')
    dados = cursor.fetchall()
    conexao.close()

    cabecalho('Alunos cadastrados')
    if not dados:
        print('Nenhum aluno cadastrado')
        print(linha())

    for aluno in dados:
        imprimirAluno(aluno)

    return dados


def buscarAlunoBanco(nome):
    """Busca pelo nome (sem diferenciar maiusculas). Retorna todos os encontrados."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT * FROM alunos WHERE nome = ?
""", (normalizarNome(nome),))
    alunos = cursor.fetchall()
    conexao.close()

    if alunos:
        for aluno in alunos:
            imprimirAluno(aluno)
    else:
        print('Aluno nao encontrado')

    return alunos


def editarIdadeBanco(nome, nova_idade):
    """Altera a idade. Retorna quantos registros foram alterados."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    UPDATE alunos
    SET idade = ?
    WHERE nome = ?
""", (nova_idade, normalizarNome(nome)))
    alterados = cursor.rowcount
    conexao.commit()
    conexao.close()

    if alterados > 0:
        print(f'Idade atualizada ({alterados} registro(s))')
    else:
        print('Aluno nao encontrado')

    return alterados


def editarPlanoBanco(nome, novo_plano):
    """Altera o plano (1 = musculacao, 2 = pilates). Retorna quantos registros mudaram."""
    if novo_plano == 1:
        novo_plano = 'musculacao'
    else:
        novo_plano = 'pilates'

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    UPDATE alunos
    SET plano = ?
    WHERE nome = ?
""", (novo_plano, normalizarNome(nome)))
    alterados = cursor.rowcount
    conexao.commit()
    conexao.close()

    if alterados > 0:
        print(f'Plano atualizado ({alterados} registro(s))')
    else:
        print('Aluno nao encontrado')

    return alterados


def excluirAlunoBanco(nome):
    """Exclui pelo nome. Retorna quantos registros foram excluidos."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    DELETE FROM alunos
    WHERE nome = ?
""", (normalizarNome(nome),))
    excluidos = cursor.rowcount
    conexao.commit()
    conexao.close()

    if excluidos > 0:
        print('Aluno excluido com sucesso')
    else:
        print('Aluno nao encontrado')

    return excluidos


def contarAlunosBanco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT COUNT(*) FROM alunos')
    total = cursor.fetchone()[0]
    conexao.close()
    return total


def atividadesAlunos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT COUNT(*) FROM alunos
    WHERE status = 'ativo'
""")
    ativos = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM alunos
    WHERE status = 'inativo'
""")
    inativos = cursor.fetchone()[0]
    conexao.close()

    cabecalho('Atividade dos alunos')
    print(f'Alunos ativos: {ativos}')
    print(f'Alunos inativos: {inativos}')

    return ativos, inativos


def alunosPorPlanoBanco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT nome FROM alunos
    WHERE plano = 'musculacao'
""")
    musculacao = cursor.fetchall()

    cursor.execute("""
    SELECT nome FROM alunos
    WHERE plano = 'pilates'
""")
    pilates = cursor.fetchall()
    conexao.close()

    cabecalho('Alunos fazendo musculacao')
    for aluno in musculacao:
        print(aluno[0])

    cabecalho('Alunos fazendo pilates')
    for aluno in pilates:
        print(aluno[0])
    print(linha())

    m = len(musculacao)
    p = len(pilates)

    cabecalho('Dados')
    print(f'Musculacao:{m} Pilates:{p}')
    print(linha())
    return m, p


def formatarMedia(valor):
    if valor is None:
        return 'sem dados'
    return f'{valor:.1f} anos'


def mediaIdadesBanco():
    """Imprime e retorna (media geral, media musculacao, media pilates).

    Cada media e None quando nao ha alunos naquele grupo.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT AVG(idade) FROM alunos
    WHERE plano = 'musculacao'
""")
    media_m = cursor.fetchone()[0]

    cursor.execute("""
    SELECT AVG(idade) FROM alunos
    WHERE plano = 'pilates'
""")
    media_p = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(idade) FROM alunos')
    media = cursor.fetchone()[0]
    conexao.close()

    cabecalho('Media de idades')
    print(f'Media geral: {formatarMedia(media)}')
    print(linha())
    print(f'Musculacao: {formatarMedia(media_m)}')
    print(linha())
    print(f'Pilates: {formatarMedia(media_p)}')
    print(linha())

    return media, media_m, media_p


def porSexoBanco():
    """Imprime e retorna (homens, mulheres). Retorna (0, 0) com o banco vazio."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT COUNT(*) FROM alunos
    WHERE sexo = 'masculino'
""")
    homens = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM alunos
    WHERE sexo = 'feminino'
""")
    mulheres = cursor.fetchone()[0]
    conexao.close()

    total = homens + mulheres
    cabecalho('Dados')
    if total == 0:
        print('Nenhum aluno cadastrado')
        return 0, 0

    homens_dados = (homens / total) * 100
    mulheres_dados = (mulheres / total) * 100

    print(f'Homens: {homens} ({homens_dados:.1f}%)')
    print(linha())
    print(f'Mulheres: {mulheres} ({mulheres_dados:.1f}%)')

    return homens, mulheres
