def leiaStatus(msg):
    while True:
        status = int(input(msg))

        if status == 1:
            status = 'ativo'
            return status
        elif status == 2:
            status = 'Inativo'
            return status
        else:
            print('Digite um valor valido')


def leiaPlano(msg):
    while True:
        plano = int(input(msg))

        if plano == 1:
            plano = 'Musculacao'
            return plano
        elif plano == 2:
            plano = 'Pilates'
            return plano
        else:
            print('Digite um valor valido')

def leiaSexo(msg):
    while True:
        sexo = str(input(msg)).lower()

        if sexo == 'm':
            sexo = 'Masculino'
            return sexo
        elif sexo == 'f':
            sexo = 'Feminino'
            return sexo
        else:
            print('Digite um valor válido')


def leiaInt(msg):
    while True:
        try:
            n = int(input(msg))
        except:
            print('Digite um valor valido')
        else:
            return n
        
def linha(tam = 42):
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
    opc = leiaInt('Escolha uma opção ')
    return opc
    