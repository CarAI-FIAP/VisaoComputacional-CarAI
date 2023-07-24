import cv2
import matplotlib.pyplot as plt
import numpy as np
from spicy import signal
import math

from CalibracaoCamera import CalibracaoCamera
from TratamentoDeImagem import *
from TransformacaoDePerspectiva import *

class FaixasDeTransito:
    # Classe para classificar as faixas de trânsito.

    def __init__(self):
        #self.calibracao = CalibracaoCamera('camera_cal', 9, 6)
        self.tratamento = TratamentoDeImagem()
        self.transformacao = TransformacaoDePerspectiva()

    def identificar_faixas(self, img):
        #out_img = np.copy(img)

        #img = self.calibracao.corrigir_distorcao(img)
        img_warped = self.transformacao.mudar_perspectiva(img)
        img_threshold = self.tratamento.binarizar_imagem(img_warped)
        img_filtrada = self.tratamento.aplicar_filtros(img_threshold)
        #img_roi = self.tratamento.desenhar_roi(img_filtrada)

        pontos, angulo = self.calcular_resultados_faixas(img_filtrada, 1100)
        out_img = self.plotar_resultados(img_warped, pontos, angulo)

        cv2.imshow('img_filtrada', self.tratamento.redimensionar_imagem(img_filtrada, 350))
        cv2.imshow('img', self.tratamento.redimensionar_imagem(img, 350))

        return out_img

    def plotar_resultados(self, img, pontos, angulo):
        out_img = np.copy(img)

        for i, ponto in enumerate(pontos):
            if i == 1:
                cor = (255, 0, 0)
            elif i == 2:
                cor = (0, 0, 255)
            else:
                cor = (0, 255, 0)

            cv2.circle(out_img, ponto, 10, cor, -1)

        print('Ângulo ABP:', angulo)

        return out_img

    def calcular_resultados_faixas(self, img, coordenada_min_y):
        y_faixas = coordenada_min_y
        y90 = coordenada_min_y + 100

        histograma = self.calcular_histograma_pista(img, y_faixas, y_faixas + 10)
        x_esquerda, x_direita = self.calcular_picos_do_histograma(histograma)

        histograma_ponto_B = self.calcular_histograma_pista(img, y90, y90 + 10)
        x_esquerda_B, _ = self.calcular_picos_do_histograma(histograma_ponto_B)

        ponto_A = (int(x_esquerda), int(y_faixas))
        ponto_B = (int(x_esquerda_B), int(y90))
        ponto_90 = (int(x_esquerda), int(y90))
        ponto_direita = (int(x_direita), int(y_faixas))

        AP = math.sqrt((ponto_90[0] - ponto_A[0])**2 + (ponto_90[1] - ponto_A[1])**2)
        BP = math.sqrt((ponto_90[0] - ponto_B[0])**2 + (ponto_90[1] - ponto_B[1])**2)

        angulo_ABP = math.degrees(math.atan(AP / BP))

        #angulo_BAP = math.degrees(math.atan(BP / AP))

        return [ponto_A, ponto_B, ponto_90, ponto_direita], angulo_ABP

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
        picos = signal.find_peaks_cwt(histograma, np.arange(1, 150), min_length=150)

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
