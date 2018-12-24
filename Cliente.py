import pygame
import pickle
import socket
import os
import time


largura = 1000
altura = 900
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("TP 9 - Projeto de bloco")
pygame.display.init()
clock = pygame.time.Clock()
pygame.font.init()
arial = pygame.font.match_font('Arial')
font = pygame.font.Font(arial, 16)

preto = (0, 0, 0)
azul = (0,0,255)
branco = (255, 255, 255)
verde_escuro = (0, 100, 0)
vermelho = (255, 0, 0)
cinza = (220, 220, 220)

s1 = pygame.surface.Surface((largura, altura))


udp_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (socket.gethostname(), 9999)


def entrada_inf_servidor():
    s1.fill(cinza)

    exibe_info_cpu()
    exibe_uso_memoria()
    exibe_uso_disco()
    exibe_uso_cpu()
    info_processos_servidor()
    arquivos()
    info_rede()


def exibe_info_cpu():
    try:
        udp_cliente.sendto('cpu'.encode(), dest)
        (msg, host) = udp_cliente.recvfrom(4096)
        lista = pickle.loads(msg)

        postion = 10
        for indice in lista:
            for i in indice:
                text = font.render("{:30}".format(i+":") + indice[i], 1, preto)
                s1.blit(text, (20, postion))
            postion += 15
        tela.blit(s1, (0, 0))
    except Exception as error:
        print(error)


def exibe_uso_memoria():

    udp_cliente.sendto('memoria'.encode(), dest)
    (msg, host) = udp_cliente.recvfrom(4096)
    memoria_servidor = pickle.loads(msg)

    mem = memoria_servidor
    larg = largura - 2 * 20

    pygame.draw.rect(tela, vermelho, (20, 150, larg, 40))
    larg = larg * mem.percent / 100
    pygame.draw.rect(tela, azul, (20, 150, larg, 40))
    total = round(mem.total / (1024 * 1024 * 1024), 2)
    texto_barra = "Uso de Memória (Total: " + str(total) + "GB) usada (" + str(mem.percent) + "%)"
    text = font.render(texto_barra, 1,preto)
    tela.blit(text, (15, 130))


def exibe_uso_disco():
    udp_cliente.sendto('hd'.encode(), dest)
    (msg, host) = udp_cliente.recvfrom(4096)
    disco_servidor = pickle.loads(msg)

    disco = disco_servidor
    larg = largura- 2 * 20

    pygame.draw.rect(tela, vermelho, (20, 220, larg, 40))
    larg = larg * disco.percent / 100
    pygame.draw.rect(tela, azul, (20, 220, larg, 40))
    total = round(disco.total / (1024 * 1024 * 1024), 2)
    texto_barra = "Uso de Disco: " + str(total) + "GB, corresponde a " + str(disco.percent) + "%"
    text = font.render(texto_barra, 1, preto)
    tela.blit(text, (20, 200))


def exibe_uso_cpu():
    udp_cliente.sendto('cpu'.encode(), dest)
    (msg, host) = udp_cliente.recvfrom(4096)
    cpu_servidor = pickle.loads(msg)

    l_cpu_percent = cpu_servidor


    s1.fill(branco)
    num_cpu = len(l_cpu_percent)
    x = y = 10
    desl = 10
    alt = 30
    larg = (s1.get_width() - 2 * y - (num_cpu + 1) * desl) / num_cpu
    d = x + desl

    for i in l_cpu_percent:
        pygame.draw.rect(s1, azul, (d, y, larg, alt))
        pygame.draw.rect(s1, vermelho, (d, y, larg, (1 - i / 100) * alt))
        texto = "Núcleo " + str(i) + "%"
        text = font.render(texto, 1, preto)
        tela.blit(text, (d, 270, larg, alt))
        d = d + larg + desl
    tela.blit(s1, (0, 285))

    for item in l_cpu_percent:
        item += item
    texto = "Porcentagem do uso de CPU " + str(item) + "%"

    text = font.render(texto, 2, preto)
    tela.blit(text, (20, 340, 300, 0))


def info_processos_servidor():
    try:
        udp_cliente.sendto('pids'.encode(), dest)
        (msg, host) = udp_cliente.recvfrom(4096)
        lista = pickle.loads(msg)

        pygame.draw.rect(tela, verde_escuro, (20, 365, 380, 2))

        texto_barra = "PROCESSOS RODANDO NO SERVIDOR"
        text = font.render(texto_barra, 1, preto)
        tela.blit(text, (20, 370))
        texto_barra = "{:<15}".format('PID') + "{:<30}".format('Nome') + "{:<25}".format('Memória')
        text = font.render(texto_barra, 1, preto)
        tela.blit(text, (20, 400))


        altura = 0

        for i in lista:
            text = font.render("{:<15}".format(i['PID']) + "{:<30}".format(i['Nome']) + "{:<25}".format(i['RSS']), 1, azul)
            tela.blit(text, (20, 425 + altura))
            altura += 15

    except Exception as error:
        print(error)


def arquivos():
    udp_cliente.sendto('arquivos'.encode(), dest)
    (msg, host) = udp_cliente.recvfrom(4096)
    try:
        lista = pickle.loads(msg)

        lista = lista
        dicionario = {}
        for i in lista[1:5]:
            if os.path.isfile(i):
                dicionario[i] =  []
                dicionario[i].append(os.stat(i).st_size)
                dicionario[i].append(os.stat(i).st_atime)
                dicionario[i].append(os.stat(i).st_mtime)

        titulo = '{:30}'.format("Tamanho")
        titulo = titulo + '{:30}'.format("Data de Criação")
        titulo = titulo + 'Nome'

        font = pygame.font.Font(arial, 16)
        text = font.render(titulo, 1, preto)
        tela.blit(text, (350, 340))

        linhas = 0
        for i in dicionario:
            kb = dicionario[i][0]/1000
            tamanho = '{:10}'.format(str('{:.2f}'.format(kb)+'KB'))
            linha_texto = "{:<20}".format(tamanho) + "{:<30}".format(time.ctime(dicionario[i][1])) + "{:<20}".format(i)

            text = font.render(linha_texto, 1, preto)
            tela.blit(text, (410, 360 + linhas))
            linhas += 20
    except Exception as error:
        font = pygame.font.Font(arial, 12)
        texto_barra = "ARQUIVO NÃO ENCONTRADO NO SERVIDOR" + str(error)
        text = font.render(texto_barra, 1, preto)
        tela.blit(text, (410, 340))
        texto_barra = str(error)
        text = font.render(texto_barra, 1, preto)
        tela.blit(text, (410, 380))


def info_rede():
    udp_cliente.sendto('rede'.encode(), dest)
    (msg, host) = udp_cliente.recvfrom(4096)
    try:
        lista = pickle.loads(msg)

        interface = lista
        nomes = []
        font = pygame.font.Font(arial, 12)
        text = font.render("INFORMAÇÃO DA SUA REDE TCP/IP", 1, preto)
        tela.blit(text, (410, 440))

        for i in interface:
            nomes.append(str(i))

        nome = 0
        redes = 0
        for i in nomes[1:3]:
            text = font.render(i, 1, preto)
            tela.blit(text, (430, 460 + nome))
            nome += 100

            for j in interface[i]:
                text = font.render("{:<12}".format('Família:') + str(j.family), 1, preto)
                tela.blit(text, (480, 480 + redes))

                text = font.render("{:<12}".format('Address:') + str(j.address), 1, preto)
                tela.blit(text, (480, 500 + redes))

                text = font.render("{:<16}".format('Netmask:') + str(j.netmask), 1, preto)
                tela.blit(text, (480, 520 + redes))

                redes += 60

    except Exception as error:
        print(error)


terminou = False
cont = 0
while not terminou:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminou = True
            pygame.display.quit()
            udp_cliente.close()
    if cont == 60:
        print("Atualizou do servidor em 60ms")
        entrada_inf_servidor()
        cont = 0

    pygame.display.update()
    clock.tick(60)
    cont = cont + 1

