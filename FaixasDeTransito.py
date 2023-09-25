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

comunicacao_arduino = False

port = configuracoes.arduino_port
rate = configuracoes.arduino_rate

if comunicacao_arduino:
    serial_arduino = serial.Serial(port, rate)

class FaixasDeTransito:
    # Classe para classificar as faixas de trânsito.

    def __init__(self):
        self.tratamento = TratamentoDeImagem()
        self.transformacao = TransformacaoDePerspectiva()

        self.fator_reducao = configuracoes.fator_reducao
        self.birds_view = True

        self.dist_max_entre_faixas_lista = []
        self.dist_max_entre_faixas = 212
        self.angulo_padrao_lista = []
        self.angulo_padrao = 40
        self.qtd_max_dados = 50 # Qtd de dados necessários para setar os valores padrão

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

        if not self.birds_view:
            img_roi = self.transformacao.desenhar_roi(img_copia)
        else:
            img_roi = self.transformacao.desenhar_roi(img_copia)

        # Alterar coordenada_min_y de acordo com a altura da img_filtrada
        if self.birds_view:
            pontos, coord_faixas, angulos, _ = self.calcular_resultados_faixas(img_filtrada, img_filtrada.shape[0] - (
                        200 // self.fator_reducao))
        else:
            if len(self.angulo_padrao_lista) == self.qtd_max_dados:
                angulo_padrao = int(np.mean(self.angulo_padrao_lista))

                pontos, coord_faixas, angulos, _ = self.calcular_resultados_faixas(img_filtrada,
                            img_filtrada.shape[0] - (200 // self.fator_reducao), angulo_padrao)

            else:
                pontos, coord_faixas, angulos, angulos_sem_correcao = self.calcular_resultados_faixas(img_filtrada,
                            img_filtrada.shape[0] - (200 // self.fator_reducao))

                if len(self.angulo_padrao_lista) < self.qtd_max_dados and coord_faixas[0] != 0 and coord_faixas[1] != 0:
                    self.angulo_padrao_lista.append(np.nanmin(angulos_sem_correcao))

        if len(angulos) > 0:
            angulo = np.mean(angulos)

        else:
            angulo = 1999

        faixa_esquerda, faixa_direita = coord_faixas

        if len(self.dist_max_entre_faixas_lista) == self.qtd_max_dados:
            self.dist_max_entre_faixas = int(np.nanmax(self.dist_max_entre_faixas_lista))
            print('dist_max:', self.dist_max_entre_faixas)

        if faixa_esquerda != 0 and faixa_direita != 0:
            offset, dist_entre_faixas = self.calcular_offset(img, [faixa_esquerda, faixa_direita])

            if len(self.dist_max_entre_faixas_lista) < self.qtd_max_dados:
                self.dist_max_entre_faixas_lista.append(dist_entre_faixas)

        elif faixa_esquerda == 0 or faixa_direita == 0:
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
                if self.birds_view:
                    cv2.imshow('Resultados', self.tratamento.redimensionar_imagem(img_resultados, 450))
                    cv2.imshow('Imagem ROI', self.tratamento.redimensionar_imagem(img_roi, 280))

                else:
                    cv2.imshow('Resultados', self.tratamento.redimensionar_imagem(img_resultados, 280))

        else:
            cv2.destroyAllWindows()

    def calcular_resultados_faixas(self, img, coordenada_min_y, debug=True):
        y_faixas = coordenada_min_y
        y90 = coordenada_min_y + (120 // self.fator_reducao)

        histograma = self.calcular_histograma_pista(img, y_faixas, y_faixas + 10)
        x_esquerda, x_direita = self.calcular_picos_do_histograma(histograma)


        if x_esquerda != 0 and x_direita != 0:
            if x_esquerda > (img.shape[1] // 2):
                x_esquerda = 0

            if x_direita < (img.shape[1] // 2):
                x_direita = 0

        coord_faixas = [x_esquerda, x_direita]

        histograma_ponto_B = self.calcular_histograma_pista(img, y90, y90 + 10)
        x_esquerda_B, x_direita_B = self.calcular_picos_do_histograma(histograma_ponto_B)

        if debug:
            print('Esquerda B (x):', x_esquerda_B)
            print('Direita B (x):', x_direita_B)

        pontos = []

        if x_esquerda != 0 and x_esquerda_B != 0:
            pontos_triangulo_esquerda = [(int(x_esquerda), int(y_faixas)), (int(x_esquerda_B), int(y90)),
                                         (int(x_esquerda), int(y90))]
            pontos.append(pontos_triangulo_esquerda)

        if x_direita != 0 and x_direita_B != 0:
            pontos_triangulo_direita = [(int(x_direita), int(y_faixas)), (int(x_direita_B), int(y90)),
                                        (int(x_direita), int(y90))]
            pontos.append(pontos_triangulo_direita)

        # Caso a curva à direita invada o outro lado
        if x_esquerda == 0 and x_direita_B == 0 and x_direita != 0 and x_esquerda_B > 20:
            pontos_triangulo_curva_direita = [(int(x_direita), int(y_faixas)), (int(x_esquerda_B), int(y90)),
                                        (int(x_direita), int(y90))]
            pontos.append(pontos_triangulo_curva_direita)

        # Caso a curva à esquerda invada o outro lado
        if x_direita == 0 and x_esquerda_B == 0 and x_esquerda != 0 and x_direita_B > 20:
            pontos_triangulo_curva_esquerda = [(int(x_esquerda), int(y_faixas)), (int(x_direita_B), int(y90)),
                                        (int(x_esquerda), int(y90))]
            pontos.append(pontos_triangulo_curva_esquerda)

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
                    angulo_BAP = int(math.degrees(math.atan(BP / AP)))
                    # print('Ângulo BAP:', angulo_BAP)

                    if x_esquerda != 0 and x_direita != 0:
                        angulos_sem_correcao.append(angulo_BAP)

                    if not (self.birds_view):
                        angulo_BAP -= self.angulo_padrao
                        angulo_BAP = abs(angulo_BAP)

                    if angulo_BAP != 0:
                        if ponto_B[0] > ponto_A[0]:
                            angulos.append(-angulo_BAP)
                        else:
                            angulos.append(angulo_BAP)

                except ZeroDivisionError:
                    return

        else:
            print('Nenhuma faixa foi encontrada. Ajuste os parâmetros para identificá-las!')

        return pontos, coord_faixas, angulos, angulos_sem_correcao

    def calcular_offset(self, img, pontos, debug=False):
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
            centro_pista = ponto_esquerda + (self.dist_max_entre_faixas / 2)

            offset = (np.abs(posicao_carro) - np.abs(centro_pista))

            if debug:
                print('\nCP:', centro_pista)
                print('offset:', offset)
                print('dist_max:', self.dist_max_entre_faixas)
                print('CI:', posicao_carro)
                print('XFD:', ponto_direita)
                print('XFE:', ponto_esquerda)

            return offset

        elif ponto_direita != 0:
            centro_pista = ponto_direita - (self.dist_max_entre_faixas / 2)

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

    def calcular_histograma_pista(self, img, altura_min, altura_max, debug=False):
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

        if debug:
            plt.plot(histograma)
            plt.title('Histograma')
            plt.show()

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
