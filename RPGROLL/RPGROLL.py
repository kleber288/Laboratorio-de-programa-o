import random
import os

class Player:
    def __init__(self, nome, vida, dano, defesa):
        self.nome = nome
        self.vida = vida
        self.dano = dano
        self.defesa = defesa

class Mob1:
    def __init__(self, vidamob, danomob):
        self.vidamob = vidamob
        self.danomob = danomob

m = Mob1(100, 25)

def rolar(lados):
    desc = int(input('Para roletar o dado digite (1): '))
    if desc == 1:
        return random.randint(1, lados)
    else:
        print('Opção inválida.')
        return 0

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')
    
v = '\033[31m'
g = '\033[32m'
a = '\033[33m'
r = '\033[0m'

nomeplayer = input('Digite seu nome/nick: ')
print(f'\n{a}----Bem vindo ao RPG ROLL {nomeplayer}!----{r}')
print(f'\n{a}----COMO JOGAR----{r}')
print(f'\nEscolha sua classe, rode o dado para dar dano e ganhar pontos de defesa. Boa sorte!')
print(f'\n{a}----CLASSES----{r}')
print(f'\n1.Guerreiro - 130 de vida / dado de 20 lados'
      f'\n2.Mago - 100 de vida / dado de 30 lados'
      f'\n3.Arqueiro - 100 de vida / dado de 15 lados / + chance de defesa')

c = 0
lados = 0

while c == 0:
    classe = int(input('\nEscolha sua classe: '))
    if classe == 1:
        print('Classe escolhida: Guerreiro!')
        p = Player(nomeplayer, 130, 0, 0)
        lados = 20
        p.defesa = 10
        c = 1
    elif classe == 2:
        print('Classe escolhida: Mago!')
        p = Player(nomeplayer, 100, 0, 0)
        lados = 30
        p.defesa = 10
        c = 1
    elif classe == 3:
        print('Classe escolhida: Arqueiro!')
        p = Player(nomeplayer, 100, 0, 0)
        lados = 15
        p.defesa = 20
        c = 1
    else:
        print('Classe inválida!')

while m.vidamob > 0 and p.vida > 0:
    input("\nPressione ENTER para continuar...")
    limpar()
    p.dano = rolar(lados)
    print(f'\nVocê causou {v}{p.dano}{r} de dano!')
    m.vidamob -= p.dano
    print(f'Vida do inimigo: {v}{m.vidamob}hp{r}')
    rolardefesa = random.randint(1, 10)
    danomob = random.randint(1, m.danomob)
    danomob -= rolardefesa
    if danomob <= rolardefesa:
        print(f'\nVocê não tomou dano!')
    elif danomob > rolardefesa:
        print(f'\nVocê tomou {v}{danomob}{r} de dano e defendeu {g}{rolardefesa}{r}')
        p.vida -= danomob
        print(f'Sua vida: {g}{p.vida}hp{r}')
    if m.vidamob <= 0:
        print(f'\n{a}----Parábens você derrotou o inimigo!----{r}')
        break
    elif p.vida <= 0:
        print(f'\n{a}----Você foi derrotado, tente novamente!----{r}')
        break
    elif p.vida <=0 and m.vidamob <=0:
        print(f'\n{a}----Parábens você derrotou o mob porém foi derrotado, tente novamente!----{r}')
        
s = 0
if s == 0:
    s = int(input(f'\nDigite (1) para sair: '))
print('saindo...')