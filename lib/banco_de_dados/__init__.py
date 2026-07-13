import sqlite3
from lib.inter import *
from time import sleep
from datetime import date

def criarBanco():
    conexao = sqlite3.connect('academia.db')
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

def cadastrarBanco(nome, idade, sexo, plano, status):
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    hoje = date.today()
    cursor.execute("""
    INSERT INTO alunos(nome, idade, sexo, plano, status, data_matricula)
    VALUES(?, ?, ?, ?, ?, ?)
""", (nome.lower(), idade, sexo.lower(), plano.lower(), status.lower(), hoje))
    
    conexao.commit()
    conexao.close()

def listarAlunosBanco():
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM alunos
    """)

    dados = cursor.fetchall()
    cabecalho('Alunos cadastrados')
    for aluno in dados:
        print(f'ID: {aluno[0]}')
        print(f'Nome: {aluno[1]}')
        print(f'Idade: {aluno[2]}')
        print(f'Sexo: {aluno[3]}')
        print(f'Plano: {aluno[4]}')
        print(f'Status: {aluno[5]}')
        print(f'Data de matricula: {aluno[6]}')
        print(linha())

    conexao.close()
    sleep(2)

def buscarAlunoBanco(nome):
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT * FROM alunos WHERE nome = ?
""",(nome,))
    
    aluno = cursor.fetchone()

    conexao.close()

    if aluno:
        print(f'ID: {aluno[0]}')
        print(f'Nome: {aluno[1]}')
        print(f'Idade: {aluno[2]}')
        print(f'Sexo: {aluno[3]}')
        print(f'Plano: {aluno[4]}')
        print(f'Status: {aluno[5]}')
        print(f'Data de matricula: {aluno[6]}')
        print(linha())
    else:
        print('Aluno nao encontrado')

    sleep(2)

def editarIdadeBanco(nome, nova_idade):
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    
    cursor.execute("""
    UPDATE alunos
    SET idade = ?
    WHERE nome = ?
""",(nova_idade, nome))
    
    conexao.commit()
    conexao.close()

def excluirAlunoBanco(nome):
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    DELETE FROM alunos
    WHERE nome = ?
""",(nome,))
    
    conexao.commit()
    conexao.close()

    if cursor.rowcount > 0:
        print('Aluno excluido com sucesso')
    
    else:
        print('Aluno não encontrado')

    sleep(2)

def editarPlanoBanco(nome, novo_plano):
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    if novo_plano == 1:
        novo_plano = 'musulacao'
    else:
        novo_plano = 'pilates' \
        ''
    cursor.execute("""
    UPDATE alunos
    SET plano = ?
    WHERE nome = ?
""",(novo_plano, nome))
    
    conexao.commit()
    conexao.close()

def contarAlunosBanco():
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT COUNT(*) FROM alunos
""")
    
    total = cursor.fetchone()
    conexao.close()
    return total[0]

def atividadesAlunos():
    conexao = sqlite3.connect('academia.db')
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

    cabecalho('Atividade dos alunos')
    print(f'Alunos ativos: {ativos}')
    print(f'Alunos inativos: {inativos}')

    return ativos, inativos

def alunosPorPlanoBanco():
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT * FROM alunos
    WHERE plano = 'musculacao'
""")
    musculacao = cursor.fetchall()
    cabecalho('Alunos fazendo musculacao')
    m = 0
    for aluno in musculacao:
        print(aluno[1])
        m += 1

    cursor.execute("""
    SELECT * FROM alunos
    WHERE plano = 'pilates'
""")
    musculacao = cursor.fetchall()
    cabecalho('Alunos fazendo pilates')
    p = 0
    for aluno in musculacao:
        print(aluno[1])
        p += 1
    print(linha())

    cabecalho('Dados')
    print(f'Musculacao:{m} Pilates:{p}')
    print(linha())
    return m, p
    
    conexao.close()

def mediaIdadesBanco():
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT AVG(idade) FROM alunos
    WHERE plano = 'musculacao'
""")
    media_m = cursor.fetchone()

    cursor.execute("""
    SELECT AVG(idade) FROM alunos
    WHERE plano = 'pilates'
""")
    media_p = cursor.fetchone()

    cursor.execute("""
    SELECT AVG(idade) FROM alunos
""")

    media = cursor.fetchone()

    cabecalho('Media de idades')
    print(f'Media geral: {media}')
    print(linha())
    print(f'Musculacao: {media_m}')
    print(linha())
    print(f'Pilates: {media_p}')
    print(linha())

    conexao.close()
    

def porSexoBanco():
    conexao = sqlite3.connect('academia.db')
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

    total = homens + mulheres
    if total == 0:
        conexao.close()
        return
    homens_dados = (homens/total) * 100
    mulheres_dados = (mulheres/total) * 100

    cabecalho('Dados')
    print(f'Homens: {homens} ({homens_dados:.1f}%)')
    print(linha())
    print(f'Mulheres: {mulheres} ({mulheres_dados:.1f}%)')

    return homens, mulheres

    conexao.close()

def atualizarBanco():
    conexao = sqlite3.connect('academia.db')
    cursor = conexao.cursor()
    cursor.execute("""
    PRAGMA table_info(alunos)
""")
    
    colunas = cursor.fetchall()
    existe = False

    for coluna in colunas:
        if coluna[1] == 'data_matricula':
            existe = True
        
    if existe:
        conexao.close()
        return

    if not existe:
        cursor.execute("""
        ALTER TABLE alunos 
        ADD COLUMN data_matricula TEXT
        """)

    conexao.commit()
    conexao.close()


    
    


    
    
    
    