
from lib.arquivo import *
from lib.inter import *
from time import sleep
from lib.banco_de_dados import *
import matplotlib.pyplot as plt
from datetime import date

criarBanco()
atualizarBanco()


while True:

    resposta = menu(['Cadastrar aluno', 'Listar alunos', 'Buscar aluno', 'Relatorios'])
    
    if resposta == 1:
        nome = str(input('Digite seu nome '))
        idade = leiaInt('Digite sua idade ')
        sexo = leiaSexo('Digite seu sexo [m/f] ')
        plano = leiaPlano('Musculação ou Pilates? [1/2] ')
        status = leiaStatus('Aluno esta ativo ou inativo [1/2] ')
        print(linha())

        cadastrarBanco(nome, idade, sexo, plano, status)

    elif resposta == 2:
        listarAlunosBanco()
        sleep(2)

    elif resposta == 3:
        cabecalho('Buscando aluno')
        nome = str(input('Digite o nome do aluno '))
        buscarAlunoBanco(nome)

    elif resposta == 4:
        resposta_relatorios = menu(['Atividade dos alunos', 'Total de alunos', 'Alunos por plano', 'Editar aluno', 'Informações de idades', 'Estatisticas por sexo'])

        if resposta_relatorios == 1:
            a, i = atividadesAlunos()
            nomes = ['Ativos', 'Inativos']
            valores = [a, i]

            plt.pie(valores, labels=nomes)

            plt.show()

            sleep(2)
        
        elif resposta_relatorios == 2:
            cabecalho('Total de alunos')
            print(f'{contarAlunosBanco():>20}')
            print(linha())

            sleep(2)
        
        elif resposta_relatorios == 3:
            cabecalho('Alunos por plano')
            m, p = alunosPorPlanoBanco()
            nomes = ['Musculacao', 'Pilates']
            valores = [m, p]

            plt.bar(nomes, valores)
            
            plt.show()
            sleep(2)
        
        elif resposta_relatorios == 4:
            resposta_editar_alunos = menu(['Alterar idade',  'Alterar plano', 'Excluir aluno'])
            
            if resposta_editar_alunos == 1:
                print(linha())
                nome = str(input('Digite o nome do aluno '))
                nova_idade = leiaInt('Digite a nova idade ')
                editarIdadeBanco(nome, nova_idade)

            elif resposta_editar_alunos == 2:
                print(linha())
                nome = str(input('Digite o nome do aluno ').lower())
                print(linha())
                novo_plano = menu(['Musculação', 'Pilates'])
                while novo_plano != 1 and novo_plano != 2:
                    novo_plano = leiaInt('Digite um valor válido!')
                editarPlanoBanco(nome, novo_plano)
                print(linha())

            elif resposta_editar_alunos == 3:
                cabecalho('Excluir aluno')
                nome = str(input('Digite o nome do aluno que deseja excluir ').lower())
                excluirAlunoBanco(nome)
                print(linha())
        
        elif resposta_relatorios == 5:
           mediaIdadesBanco()
           sleep(2)
        
        elif resposta_relatorios == 6:
            h, m = porSexoBanco()

            nomes = ['Homens', 'Mulheres']
            valores = [h, m]

            plt.pie(valores, labels=nomes)

            plt.show()

            sleep(2)

        
        
            
       



            
            





