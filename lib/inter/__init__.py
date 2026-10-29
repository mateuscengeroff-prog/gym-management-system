"""Funcoes de interface de terminal (leitura de dados e formatacao)."""


def leiaInt(msg):
    """Le um numero inteiro, repetindo a pergunta ate a entrada ser valida.

    Apenas ValueError e tratado: EOFError e KeyboardInterrupt sobem para o
    programa principal, que encerra de forma limpa (antes, um `except:`
    generico engolia o EOF e o programa entrava em loop infinito).
    """
    while True:
        try:
            n = int(input(msg))
        except ValueError:
            print('Digite um valor valido')
        else:
            return n


def leiaStatus(msg):
    while True:
        status = leiaInt(msg)

        if status == 1:
            return 'ativo'
        elif status == 2:
            return 'inativo'
        else:
            print('Digite um valor valido')


def leiaPlano(msg):
    while True:
        plano = leiaInt(msg)

        if plano == 1:
            return 'musculacao'
        elif plano == 2:
            return 'pilates'
        else:
            print('Digite um valor valido')


def leiaSexo(msg):
    while True:
        sexo = str(input(msg)).strip().lower()

        if sexo == 'm':
            return 'masculino'
        elif sexo == 'f':
            return 'feminino'
        else:
            print('Digite um valor valido')


def leiaNome(msg):
    """Le um nome nao vazio."""
    while True:
        nome = str(input(msg)).strip()

        if nome:
            return nome
        print('O nome nao pode ficar em branco')


def leiaIdade(msg, minimo=1, maximo=120):
    """Le uma idade inteira dentro de uma faixa plausivel."""
    while True:
        idade = leiaInt(msg)

        if minimo <= idade <= maximo:
            return idade
        print(f'Digite uma idade entre {minimo} e {maximo}')


def linha(tam=42):
    return '-' * tam


def cabecalho(txt):
    print(linha())
    print(txt.center(42))
    print(linha())


def menu(lista):
    c = 1
    for item in lista:
        print(f'{c} - {item}')
        c += 1
    print(linha())
    opc = leiaInt('Escolha uma opcao ')
    return opc
