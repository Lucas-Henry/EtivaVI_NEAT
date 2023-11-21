import os  # integração das imagens com o código
import random  # Randomização dos canos

import neat  # Rede Neural
import pygame  # criação de jogos

# Variáveis da Inteligência Artificial
ia_jogando = False
geracao = 0

# Largura e altura da janela do jogo
TELA_LARGURA = 500
TELA_ALTURA = 800

# Imangens dos elementos que compoem o jogo
IMAGEM_CANO = pygame.transform.scale2x(
    pygame.image.load(os.path.join("img", "pipe.png")))
IMAGEM_CHAO = pygame.transform.scale2x(
    pygame.image.load(os.path.join("img", "base.png")))
IMAGEM_BACKGROUND = pygame.transform.scale2x(
    pygame.image.load(os.path.join("img", "bg.png")))
IMAGENS_PASSAROS = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("img", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("img", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("img", "bird3.png")))
]
# Configuração de fonte de texto
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont("comicsansms", 30)

VELOCIDADE_jOGO = 5 


class Passaro:
    # Rotação do pássaro
    IMGS = IMAGENS_PASSAROS
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x  # Posição do pássaro no eixo x
        self.y = y  # Posição do pássaro no eixo y
        self.angulo = 0
        self.velocidade = 0  # velocidade no eixo y
        self.altura = self.y
        self.tempo = 0  # Duração da rotação
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):  # Velocidade do pulo
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):  # Movimenta o pássaro no eixo y
        # Calculo do deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # Restrição de deslocamento
        if deslocamento > 16:
            deslocamento = 16  # Valor máximo no eixo y
        elif deslocamento < 0:
            deslocamento -= 2  # Ganho no pulo

        self.y += deslocamento  # Movimento no eixo y

        # Ângulo do pássaro/Animação de movimento
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):  # Anima o movimento das asas e desenha o pássaro
        self.contagem_imagem += 1
        # Define qual das imagens do pássaro será usada(movimento das asas)
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # Se o pássaro cair, sem movimento das asas
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # Cria um retângulo em volta do pássaro para rotacionar
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(
            topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)

        # Desenha o pássaro (imagem, posição)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):  # Mascara de colisão do pássaro
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200  # Distância do cano de baixo para o cano de cima
    VELOCIDADE = VELOCIDADE_jOGO  # Velocidade do cano no eixo x

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0  # Posição do cano de cima no eixo y
        self.pos_bas = 0  # Posição do cano de baixo no eixo y
        self.CANO_TOPO = pygame.transform.flip(
            IMAGEM_CANO, False, True)  # (imagem, eixo x, eixo y)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False  # Verifica se o pássaro já passou do cano
        self.definir_altura()  # Sorteia a altura

    def definir_altura(self):
        # Define como os canos vão aparecer de forma randômica
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):  # Movimento dos canos no eixo x
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):  # Desenha o cano de cima e o cano de baixo
        # (imagem, posição que nesse caso é uma tupla)
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        # Verifica a colisão do pássaro com o cano de cima e o cano de baixo
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        # calculo de distância para verificar colisão
        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        # Verifica se tem dois pixels iguais do passaro com o cano do topo
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)

        # Verifica se tem dois pixels iguais do passaro com o cano da base
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if topo_ponto or base_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = VELOCIDADE_jOGO
    LARGURA = IMAGEM_CHAO.get_width()
    ALTURA = IMAGEM_CHAO.get_height()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0  # Chão 1
        self.x2 = self.LARGURA  # Chão 2

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        # Movimento dos Chão 1 e Chão 2
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(
        f"Pontuação: {pontos}", 1, (255, 255, 255))

    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    if ia_jogando:
        texto_ia = FONTE_PONTOS.render(
            f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto_ia, (10, 10))

    chao.desenhar(tela)

    pygame.display.update()  # atualiza a tela


def main(genomas, config):  # Fitness function kkkk (que código feio, namoral)
    global geracao, ia_jogando, caminho_config, lista_genomas
    if ia_jogando:
        geracao += 1
    # Genoma -> Conjunto de genes que uma determinada espécie possui

    if ia_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))
    else:
        passaros = [Passaro(230, 350)]
    canos = [Cano(700)]
    chao = Chao(730)
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    # Interação do usuário com o jogo
    rodando = True
    while rodando:
        relogio.tick(30)
        chao.mover()
        # Interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  # Apertou X, suspende a execução
                rodando = False
                pygame.quit()
                quit()
            # Ao apertar a barra de espaço, o pássaro pula
            if not ia_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

                    if evento.key == pygame.K_LCTRL:
                        rodando = False
                        ia_jogando = True
                        geracao = 0
                        rodar(caminho_config)

            elif ia_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_LCTRL:
                        rodando = True
                        ia_jogando = False
                        main(None, None)

        if ia_jogando:
            indice_cano = 0
            if len(passaros) > 0:
                if len(canos) > 1 and passaros[0].x > (
                        canos[0].x + canos[0].CANO_TOPO.get_width()):
                    indice_cano = 1
            else:
                rodando = False
                break

        # Movimentação dos objetos do jogo
        for i, passaro in enumerate(passaros):  # Movimentação dos pássaros
            passaro.mover()
            if ia_jogando:
                # Aumentar o fitness do passaro
                lista_genomas[i].fitness += 0.1
                # Cálculo para a decisão de pular ou não pular
                output = redes[i].activate(
                    (passaro.y,
                     abs(passaro.y - canos[indice_cano].altura),
                     abs(passaro.y - canos[indice_cano].pos_base)))
                # output entre -1 e 1
                if output[0] > 0.5:
                    passaro.pular()

        # Adicionar e remover passaros e canos
        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                # Verificação se houve colisão do passaro com o cano
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if not ia_jogando:
                        rodando = False
                        rodar(caminho_config)

                    if ia_jogando:
                        # Remove pontuação dos pássaros que colidirem nos canos
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                # Verifica se os pássaros passaram do cano
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True

            cano.mover()
            # Exclusão dos canos da tela
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
            # Aumentar a pontuação dos passaros caso passem do cano
            if ia_jogando:
                for genoma in lista_genomas:
                    genoma.fitness += 5

        for cano in remover_canos:
            canos.remove(cano)

        # Remover pássaros que batem no chão ou no topo
        tamanho_passaro = passaro.imagem.get_height()
        if ia_jogando:
            for i, passaro in enumerate(passaros):
                if (passaro.y + tamanho_passaro) > chao.y or passaro.y < 0:
                    passaros.pop(i)
                    if ia_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)

        # Desenha todos os objetos na tela
        desenhar_tela(tela, passaros, canos, chao, pontos)


def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    pop = neat.Population(config)

    # Estatísticas
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())

    if ia_jogando:
        pop.run(main, 50)
    else:
        main(None, None)


# Só vai rodar o código se o usuário executar manualmente
if __name__ == "__main__":
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, "config.txt")
    rodar(caminho_config)
# Esse método é bom pra não executar tudo caso o usuário importe o arquivo
