from time import sleep

from lib.inter import *
from lib.banco_de_dados import *


def mostrarGrafico(tipo, nomes, valores, titulo):
    """Mostra um grafico de pizza ou de barras com o Matplotlib.

    O grafico e pulado quando todos os valores sao zero (o grafico de pizza
    falha com o banco vazio). Cada grafico usa uma figura nova, que e fechada
    depois, para os graficos nao se sobreporem.
    """
    if sum(valores) == 0:
        print('Sem dados para gerar o grafico')
        return

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    if tipo == 'pizza':
        ax.pie(valores, labels=nomes, autopct='%1.0f%%')
    else:
        ax.bar(nomes, valores)
    ax.set_title(titulo)
    plt.show()
    plt.close(fig)


def main():
    criarBanco()
    atualizarBanco()

    while True:

        resposta = menu(['Cadastrar aluno', 'Listar alunos', 'Buscar aluno', 'Relatorios', 'Sair'])

        if resposta == 1:
            nome = leiaNome('Digite seu nome ')
            idade = leiaIdade('Digite sua idade ')
            sexo = leiaSexo('Digite seu sexo [m/f] ')
            plano = leiaPlano('Musculacao ou Pilates? [1/2] ')
            status = leiaStatus('Aluno esta ativo ou inativo [1/2] ')
            print(linha())

            cadastrarBanco(nome, idade, sexo, plano, status)

        elif resposta == 2:
            listarAlunosBanco()
            sleep(2)

        elif resposta == 3:
            cabecalho('Buscando aluno')
            nome = leiaNome('Digite o nome do aluno ')
            buscarAlunoBanco(nome)
            sleep(2)

        elif resposta == 4:
            resposta_relatorios = menu(['Atividade dos alunos', 'Total de alunos', 'Alunos por plano', 'Editar aluno', 'Informacoes de idades', 'Estatisticas por sexo'])

            if resposta_relatorios == 1:
                a, i = atividadesAlunos()
                mostrarGrafico('pizza', ['Ativos', 'Inativos'], [a, i], 'Atividade dos alunos')
                sleep(2)

            elif resposta_relatorios == 2:
                cabecalho('Total de alunos')
                print(f'{contarAlunosBanco():>20}')
                print(linha())
                sleep(2)

            elif resposta_relatorios == 3:
                m, p = alunosPorPlanoBanco()
                mostrarGrafico('barras', ['Musculacao', 'Pilates'], [m, p], 'Alunos por plano')
                sleep(2)

            elif resposta_relatorios == 4:
                resposta_editar_alunos = menu(['Alterar idade', 'Alterar plano', 'Excluir aluno'])

                if resposta_editar_alunos == 1:
                    print(linha())
                    nome = leiaNome('Digite o nome do aluno ')
                    nova_idade = leiaIdade('Digite a nova idade ')
                    editarIdadeBanco(nome, nova_idade)

                elif resposta_editar_alunos == 2:
                    print(linha())
                    nome = leiaNome('Digite o nome do aluno ')
                    print(linha())
                    novo_plano = menu(['Musculacao', 'Pilates'])
                    while novo_plano != 1 and novo_plano != 2:
                        novo_plano = leiaInt('Digite um valor valido! ')
                    editarPlanoBanco(nome, novo_plano)
                    print(linha())

                elif resposta_editar_alunos == 3:
                    cabecalho('Excluir aluno')
                    nome = leiaNome('Digite o nome do aluno que deseja excluir ')
                    excluirAlunoBanco(nome)
                    print(linha())
                sleep(2)

            elif resposta_relatorios == 5:
                mediaIdadesBanco()
                sleep(2)

            elif resposta_relatorios == 6:
                h, m = porSexoBanco()
                mostrarGrafico('pizza', ['Homens', 'Mulheres'], [h, m], 'Alunos por sexo')
                sleep(2)

        elif resposta == 5:
            print('Encerrando o sistema. Ate logo!')
            break


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: encerra sem mostrar traceback.
        print('\nEncerrando o sistema.')
