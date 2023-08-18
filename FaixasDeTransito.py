import cv2
import matplotlib.pyplot as plt
import numpy as np
from spicy import signal
import math
import serial
import time

from CalibracaoCamera import CalibracaoCamera
from TratamentoDeImagem import *
from TransformacaoDePerspectiva import *

comunicacao_arduino = False

port = 'COM6'
rate = 115200

if comunicacao_arduino:
    serial_arduino = serial.Serial(port, rate)
    time.sleep(0.1)

class FaixasDeTransito:
    # Classe para classificar as faixas de trânsito.

    def __init__(self, fator_reducao):
        self.fator_reducao = fator_reducao
        self.birds_view = True

        #self.calibracao = CalibracaoCamera('camera_cal', 9, 6)
        self.tratamento = TratamentoDeImagem()
        self.transformacao = TransformacaoDePerspectiva(fator_reducao)

    def fechar_conexao(self):
        serial_arduino.close()

    def enviar_dados_para_arduino(self, dados):
        angulo, esquerda_x, direita_x, offset = dados
        dados_enviar = f'{angulo},{esquerda_x},{direita_x},{offset}\n'

        serial_arduino.write(dados_enviar.encode())
        time.sleep(0.1)

        dados_recebidos = serial_arduino.readline().decode('utf-8').strip()
        print(f'Dados recebidos pelo Arduino: {dados_recebidos}')

    def identificar_faixas(self, img, debug=True):
        img_copia = np.copy(img)
        #img = self.calibracao.corrigir_distorcao(img)

        if self.birds_view:
            img = self.transformacao.mudar_perspectiva(img)

        #img_threshold = self.tratamento.binarizar_imagem(img)
        img_threshold = self.tratamento.binarizar_imagem(img)

        img_filtrada = self.tratamento.aplicar_filtros(img_threshold)

        if not(self.birds_view):
            img_roi = self.transformacao.desenhar_roi(img_copia)
        else:
            img_roi = self.transformacao.desenhar_roi(img_copia)

        # Alterar coordenada_min_y de acordo com a altura da img_filtrada
        if self.birds_view:
            pontos, coord_faixas, angulos = self.calcular_resultados_faixas(img_filtrada, img_filtrada.shape[0] - (200 // self.fator_reducao))
        else:
            pontos, coord_faixas, angulos = self.calcular_resultados_faixas(img_filtrada, img_filtrada.shape[0] - (150 // self.fator_reducao))

        if len(angulos) > 1 and (abs(abs(angulos[0]) - abs(angulos[1])) > 10):
            angulo = int(np.nanmax(angulos))
        else:
            angulo = int(np.nanmin(angulos))

        if coord_faixas[0] and coord_faixas[1]:
            offset = int(self.calcular_offset(img, [coord_faixas[0], coord_faixas[1]]))
        else:
            offset = None

        dados = (angulo, coord_faixas[0], coord_faixas[1], offset)

        if comunicacao_arduino:
            self.enviar_dados_para_arduino(dados)
        else:
            print(dados)

        if debug:
            out_img = np.copy(img)

            print('\nOffset: ', offset)
            print('Ângulos: ', angulos)
            print('Ângulo ABP:', angulo)
            print('Esquerda (x): ', coord_faixas[0])
            print('Direita (x): ', coord_faixas[1])

            for i, pontos_triangulo in enumerate(pontos):
                for j, ponto in enumerate(pontos_triangulo):
                    if j == 1:
                        cor = (255, 0, 0)
                    elif j == 2:
                        cor = (0, 0, 255)
                    else:
                        cor = (0, 255, 0)

                    tamanho_ponto = 16 // self.fator_reducao
                    cv2.circle(out_img, ponto, tamanho_ponto, cor, -1)

            altura_img, largura_img = out_img.shape[:2]
            espessura_linha = 16 // self.fator_reducao
            cv2.line(out_img, (largura_img // 2, 0), (largura_img // 2, altura_img), (0, 0, 0), espessura_linha)

            img_resultados = self.tratamento.juntar_videos([img_filtrada, out_img])

            if self.fator_reducao > 4:
                #cv2.imshow('img', img)
                #cv2.imshow('img_filtrada', img_filtrada)
                #cv2.imshow('out_img', out_img)
                cv2.imshow('Imagem ROI', img_roi)
                cv2.imshow('Resultados', img_resultados)

            else:
                #cv2.imshow('img', self.tratamento.redimensionar_imagem(img, 250))
                #cv2.imshow('img_filtrada', self.tratamento.redimensionar_imagem(img_filtrada, 280))
                #cv2.imshow('out_img', self.tratamento.redimensionar_imagem(out_img, 280))
                cv2.imshow('Imagem ROI', self.tratamento.redimensionar_imagem(img_roi, 280))
                cv2.imshow('Resultados', self.tratamento.redimensionar_imagem(img_resultados, 280))


        else:
            cv2.destroyAllWindows()

    def calcular_resultados_faixas(self, img, coordenada_min_y):
        y_faixas = coordenada_min_y
        y90 = coordenada_min_y + (100 // self.fator_reducao)

        histograma = self.calcular_histograma_pista(img, y_faixas, y_faixas + 10)
        x_esquerda, x_direita = self.calcular_picos_do_histograma(histograma)

        coord_faixas = [x_esquerda, x_direita]

        histograma_ponto_B = self.calcular_histograma_pista(img, y90, y90 + 10)
        x_esquerda_B, x_direita_B = self.calcular_picos_do_histograma(histograma_ponto_B)

        pontos = []

        if x_esquerda != 0 or x_esquerda_B != 0:
            pontos_triangulo_esquerda = [(int(x_esquerda), int(y_faixas)), (int(x_esquerda_B), int(y90)), (int(x_esquerda), int(y90))]
            pontos.append(pontos_triangulo_esquerda)
        #else:
            #print('Curva à esquerda')

        if x_direita != 0 or x_direita_B != 0:
            pontos_triangulo_direita = [(int(x_direita), int(y_faixas)), (int(x_direita_B), int(y90)), (int(x_direita), int(y90))]
            pontos.append(pontos_triangulo_direita)
        #else:
            #print('Curva à direita')

        angulos = []

        angulo_padrao = 0

        # Verificar se existem pontos identificados
        if pontos:
            for pontos_triangulo in pontos:
                ponto_A, ponto_B, ponto_90 = pontos_triangulo

                AP = math.sqrt((ponto_90[0] - ponto_A[0]) ** 2 + (ponto_90[1] - ponto_A[1]) ** 2)
                BP = math.sqrt((ponto_90[0] - ponto_B[0]) ** 2 + (ponto_90[1] - ponto_B[1]) ** 2)

                try:
                    #angulo_ABP = math.degrees(math.atan(AP / BP))

                    angulo_BAP = math.degrees(math.atan(BP / AP))

                    if not(self.birds_view):
                        angulo_BAP -= angulo_padrao

                    angulos.append(angulo_BAP)

                except ZeroDivisionError:
                    return

        else:
            print('Nenhuma faixa foi encontrada. Ajuste os parâmetros para identificá-las!')

        return pontos, coord_faixas, angulos

    def calcular_offset(self, img, pontos):
        posicao_carro = img.shape[1] / 2

        if len(pontos) == 2:
            centro_pista = (pontos[1] - pontos[0]) / 2 + pontos[0]

            # Offset do centro do carro para o centro da pista (em pixels)
            offset = (np.abs(posicao_carro) - np.abs(centro_pista))

            return offset

        else:
            return None

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

        #plt.plot(histograma)
        #plt.title('Histograma')
        #plt.show()

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

        return pico_esquerda, pico_direita

# © 2023 CarAI.
