import cv2
import matplotlib.pyplot as plt
import numpy as np
from spicy import signal
import math
import serial
import time

from TratamentoDeImagem import *
from TransformacaoDePerspectiva import *
from Configuracoes import *

configuracoes = Configuracoes()

comunicacao_arduino = configuracoes.comunicacao_serial_habilitada

port = configuracoes.arduino_port
rate = configuracoes.arduino_rate

if configuracoes.comunicacao_serial_habilitada:
    serial_arduino = serial.Serial(port, rate)

dist_max_entre_faixas = []
angulo_padrao_lista = []

# Qtd de dados necessários para setar os valores do ângulo padrão e da distância entre as faixas
qtd_max_dados = 50 


class FaixasDeTransito:
    # Classe para classificar as faixas de trânsito.

    def __init__(self):
        self.fator_reducao = configuracoes.fator_reducao
        self.birds_view = configuracoes.perspectiva_habilitada

        self.tratamento = TratamentoDeImagem()
        self.transformacao = TransformacaoDePerspectiva()

    def fechar_conexao(self):
        serial_arduino.close()

    def enviar_dados_para_arduino(self, dados, debug=False):
        angulo, esquerda_x, direita_x, offset = dados
        dados_enviar = f'{angulo},{esquerda_x},{direita_x},{offset}\n'

        serial_arduino.write(dados_enviar.encode())
        time.sleep(0.01)

        if debug:
            dados_recebidos = serial_arduino.readline().decode('utf-8').strip()
            print(f'\n{dados_recebidos}', end='')

    def identificar_faixas(self, img, debug=True, prints=True):
        global offset

        img_copia = np.copy(img)

        if self.birds_view:
            img = self.transformacao.mudar_perspectiva(img)

        img_threshold = self.tratamento.binarizar_imagem(img)

        img_filtrada = self.tratamento.aplicar_filtros(img_threshold)

        if not (self.birds_view):
            img_roi = self.transformacao.desenhar_roi(img_copia)
        else:
            img_roi = self.transformacao.desenhar_roi(img_copia)

        # Alterar coordenada_min_y de acordo com a altura da img_filtrada
        if self.birds_view:
            pontos, coord_faixas, angulos, _ = self.calcular_resultados_faixas(img_filtrada, img_filtrada.shape[0] - (
                        200 // self.fator_reducao))
        else:
            print(len(angulo_padrao_lista))
            if len(angulo_padrao_lista) == qtd_max_dados:
                angulo_padrao = int(np.mean(angulo_padrao_lista))

                pontos, coord_faixas, angulos, _ = self.calcular_resultados_faixas(img_filtrada,
                            img_filtrada.shape[0] - (200 // self.fator_reducao), angulo_padrao)

            else:
                pontos, coord_faixas, angulos, angulos_sem_correcao = self.calcular_resultados_faixas(img_filtrada,
                            img_filtrada.shape[0] - (200 // self.fator_reducao))

                if len(angulo_padrao_lista) < qtd_max_dados and coord_faixas[0] != 0 and coord_faixas[1] != 0:
                    angulo_padrao_lista.append(np.nanmin(angulos_sem_correcao))

        if len(angulos) < 1:
            angulo = None
        else:
            angulo = int(np.nanmin(angulos))

        faixa_esquerda, faixa_direita = coord_faixas

        if faixa_esquerda != 0 and faixa_direita != 0:
            offset, dist_entre_faixas = self.calcular_offset(img, [faixa_esquerda, faixa_direita])

            if len(dist_max_entre_faixas) < qtd_max_dados:
                dist_max_entre_faixas.append(dist_entre_faixas)

        elif faixa_esquerda == 0 or faixa_direita == 0:
            dist_max = int(np.nanmax(dist_max_entre_faixas))

            if dist_max:
                offset = self.calcular_offset(img, [faixa_esquerda, faixa_direita], dist_max)
            else:
                offset = self.calcular_offset(img, [faixa_esquerda, faixa_direita])

        else:
            offset = 2000

        # with open('valores_offset.txt', 'a') as arquivo:
        # arquivo.write(f'{offset_esquerda} | {offset_direita} | {offset} | {angulo}\n')

        dados = (angulo, faixa_esquerda, faixa_direita, offset)

        if comunicacao_arduino:
            self.enviar_dados_para_arduino(dados)

        if debug:
            out_img = np.copy(img)

            if prints:
                print('\nOffset: ', offset)
                print('Ângulos: ', angulos)
                print('Ângulo ABP:', angulo)
                print('Esquerda (x): ', faixa_esquerda)
                print('Direita (x): ', faixa_direita)

            for i, pontos_triangulo in enumerate(pontos):
                for j, ponto in enumerate(pontos_triangulo):
                    if j == 1:
                        cor = (255, 0, 0)
                    elif j == 2:
                        cor = (0, 0, 255)
                    else:
                        cor = (0, 255, 0)

                    tamanho_ponto = 12 // self.fator_reducao
                    cv2.circle(out_img, ponto, tamanho_ponto, cor, -1)

            altura_img, largura_img = out_img.shape[:2]
            espessura_linha = 12 // self.fator_reducao
            cv2.line(out_img, (largura_img // 2, 0), (largura_img // 2, altura_img), (0, 0, 0), espessura_linha)

            img_resultados = self.tratamento.juntar_videos([img_filtrada, out_img])

            if self.fator_reducao > 4:
                cv2.imshow('Resultados', img_resultados)

                if self.birds_view:
                    cv2.imshow('Imagem ROI', img_roi)

            else:
                cv2.imshow('Resultados', self.tratamento.redimensionar_imagem(img_resultados, 280))

                if self.birds_view:
                    cv2.imshow('Imagem ROI', self.tratamento.redimensionar_imagem(img_roi, 280))

        else:
            cv2.destroyAllWindows()

    def calcular_resultados_faixas(self, img, coordenada_min_y, angulo_padrao_medio=40, debug=False):
        y_faixas = coordenada_min_y
        y90 = coordenada_min_y + (120 // self.fator_reducao)

        histograma = self.calcular_histograma_pista(img, y_faixas, y_faixas + 10)
        x_esquerda, x_direita = self.calcular_picos_do_histograma(histograma)

        coord_faixas = [x_esquerda, x_direita]

        histograma_ponto_B = self.calcular_histograma_pista(img, y90, y90 + 10)
        x_esquerda_B, x_direita_B = self.calcular_picos_do_histograma(histograma_ponto_B)

        pontos = []

        if x_esquerda != 0 or x_esquerda_B != 0:
            pontos_triangulo_esquerda = [(int(x_esquerda), int(y_faixas)), (int(x_esquerda_B), int(y90)),
                                         (int(x_esquerda), int(y90))]
            pontos.append(pontos_triangulo_esquerda)
        # else:
        # print('Curva à esquerda')

        if x_direita != 0 or x_direita_B != 0:
            pontos_triangulo_direita = [(int(x_direita), int(y_faixas)), (int(x_direita_B), int(y90)),
                                        (int(x_direita), int(y90))]
            pontos.append(pontos_triangulo_direita)
        # else:
        # print('Curva à direita')

        angulos = []

        angulos_sem_correcao = []

        # Verificar se existem pontos identificados
        if pontos:
            for pontos_triangulo in pontos:
                ponto_A, ponto_B, ponto_90 = pontos_triangulo

                AP = math.sqrt((ponto_90[0] - ponto_A[0]) ** 2 + (ponto_90[1] - ponto_A[1]) ** 2)
                BP = math.sqrt((ponto_90[0] - ponto_B[0]) ** 2 + (ponto_90[1] - ponto_B[1]) ** 2)

                try:
                    # angulo_ABP = math.degrees(math.atan(AP / BP))
                    angulo_BAP = math.degrees(math.atan(BP / AP))
                    # print('Ângulo BAP:', angulo_BAP)

                    if x_esquerda != 0 and x_direita != 0:
                        angulos_sem_correcao.append(angulo_BAP)

                    if not (self.birds_view):
                        angulo_BAP -= angulo_padrao_medio
                        angulo_BAP = abs(angulo_BAP)

                    if angulo_BAP != 0:
                        if x_esquerda == 0:
                            angulos.append(-angulo_BAP)
                        else:
                            angulos.append(angulo_BAP)

                except ZeroDivisionError:
                    return

        else:
            print('Nenhuma faixa foi encontrada. Ajuste os parâmetros para identificá-las!')

        return pontos, coord_faixas, angulos, angulos_sem_correcao

    def calcular_offset(self, img, pontos, dist_max_entre_faixas=533, debug=False):
        posicao_carro = img.shape[1] / 2

        ponto_esquerda, ponto_direita = pontos

        if ponto_esquerda != 0 and ponto_direita != 0:
            centro_pista = (ponto_direita - ponto_esquerda) / 2 + ponto_esquerda

            # distancia = (ponto_direita - ponto_esquerda)
            # print(distancia)

            # Offset do centro do carro para o centro da pista (em pixels)
            offset = (np.abs(posicao_carro) - np.abs(centro_pista))

            dist_entre_faixas = (np.abs(ponto_direita) - np.abs(ponto_esquerda))

            if debug:
                print('\nCP:', centro_pista)
                print('offset:', offset)
                print('XFD:', ponto_direita)
                print('XFE:', ponto_esquerda)

            return offset, dist_entre_faixas

        elif ponto_esquerda != 0:
            centro_pista = ponto_esquerda + (dist_max_entre_faixas / 2)

            offset = (np.abs(posicao_carro) - np.abs(centro_pista))

            if debug:
                print('\nCP:', centro_pista)
                print('offset:', offset)
                print('dist_max:', dist_max_entre_faixas)
                print('CI:', posicao_carro)
                print('XFD:', ponto_direita)
                print('XFE:', ponto_esquerda)

            return offset

        elif ponto_direita != 0:
            centro_pista = ponto_direita - (dist_max_entre_faixas / 2)

            offset = (np.abs(posicao_carro) - np.abs(centro_pista))

            if debug:
                print('\nCP:', centro_pista)
                print('offset:', offset)
                print('CI:', posicao_carro)
                print('XFD:', ponto_direita)
                print('XFE:', ponto_esquerda)

            return offset

        else:
            offset = 2000

            return offset

    def calcular_histograma_pista(self, img, altura_min, altura_max):
        """
        Calcula o histograma das projeções verticais da imagem em uma faixa de altura específica.

        Parâmetro(s):
            img (np.array): Imagem de entrada.
            altura_min (int): Altura mínima da faixa de interesse para calcular o histograma.
            altura_max (int): Altura máxima da faixa de interesse para calcular o histograma.

        Retorno(s):
            histograma (np.array): Histograma das projeções verticais da imagem.
        """
        histograma = np.sum(img[int(altura_min):int(altura_max), :], axis=0)

        # plt.plot(histograma)
        # plt.title('Histograma')
        # plt.show()

        return histograma

    def calcular_picos_do_histograma(self, histograma):
        """
        Calcula os picos do histograma para identificar a posição da faixa de trânsito.

        Parâmetro(s):
            histograma (np.array): Histograma da imagem.

        Retorno(s):
            pico_esquerda (int): Pico do lado esquerdo do histograma.
            pico_direita (int): Pico do lado direito do histograma.
        """
        picos = signal.find_peaks_cwt(histograma, np.arange(1, 100), min_length=150)

        ponto_medio = int(histograma.shape[0] / 2)

        if len(picos) > 1:
            # Caso mais de dois picos sejam encontrados, selecionamos apenas o mais à esquerda e o mais à direita
            pico_esquerda, *_, pico_direita = picos

        # Caso contrário, escolhemos os pontos mais altos nas segmentações à esquerda e à direita do centro
        else:
            pico_esquerda = np.argmax(histograma[:ponto_medio])
            pico_direita = np.argmax(histograma[ponto_medio:]) + ponto_medio

            if pico_direita == ponto_medio:
                pico_direita = 0

        return pico_esquerda, pico_direita

# © 2023 CarAI.
