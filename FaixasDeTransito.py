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
        img_roi = self.transformacao.desenhar_roi(img)

        # Alterar coordenada_min_y de acordo com a altura da img_filtrada
        pontos, angulo = self.calcular_resultados_faixas(img_filtrada, img_filtrada.shape[0] - 150)
        out_img = self.plotar_resultados(img_warped, pontos, angulo)

        cv2.imshow('img_filtrada', self.tratamento.redimensionar_imagem(img_filtrada, 350))
        #plt.imshow(img_filtrada)
        #plt.show()

        cv2.imshow('img_roi', self.tratamento.redimensionar_imagem(img_roi, 350))
        cv2.imshow('img', self.tratamento.redimensionar_imagem(img, 350))

        return out_img

    def plotar_resultados(self, img, pontos, angulo):
        out_img = np.copy(img)

        altura_img, largura_img = out_img.shape[:2]
        cv2.line(out_img, (largura_img // 2, 0), (largura_img // 2, altura_img), (0, 0, 0), 10)

        for i, pontos_triangulo in enumerate(pontos):
            for j, ponto in enumerate(pontos_triangulo):
                if j == 1:
                    cor = (255, 0, 0)
                elif j == 2:
                    cor = (0, 0, 255)
                else:
                    cor = (0, 255, 0)

                cv2.circle(out_img, ponto, 10, cor, -1)

        if angulo == 0:
            print('Não foi possível calcular o ângulo! Ajuste os parâmetros para identificar as faixas')
        else:
            print('Ângulo ABP:', angulo)
            print('')

        return out_img

    def calcular_resultados_faixas(self, img, coordenada_min_y):
        y_faixas = coordenada_min_y
        y90 = coordenada_min_y + 100

        histograma = self.calcular_histograma_pista(img, y_faixas, y_faixas + 10)
        x_esquerda, x_direita = self.calcular_picos_do_histograma(histograma)

        print('Esquerda (x):', x_esquerda)
        print('Direita (x):', x_direita)

        histograma_ponto_B = self.calcular_histograma_pista(img, y90, y90 + 10)
        x_esquerda_B, x_direita_B = self.calcular_picos_do_histograma(histograma_ponto_B)

        pontos = []

        if x_esquerda != 0 or x_esquerda_B != 0:
            pontos_triangulo_esquerda = [(int(x_esquerda), int(y_faixas)), (int(x_esquerda_B), int(y90)), (int(x_esquerda), int(y90))]
            pontos.append(pontos_triangulo_esquerda)
        else:
            print('Curva à esquerda')

        if x_direita != 0 or x_direita_B != 0:
            pontos_triangulo_direita = [(int(x_direita), int(y_faixas)), (int(x_direita_B), int(y90)), (int(x_direita), int(y90))]
            pontos.append(pontos_triangulo_direita)
        else:
            print('Curva à direita')

        angulos = []

        # Verificar se existem pontos identificados
        if pontos:
            for pontos_triangulo in pontos:
                ponto_A, ponto_B, ponto_90 = pontos_triangulo

                AP = math.sqrt((ponto_90[0] - ponto_A[0]) ** 2 + (ponto_90[1] - ponto_A[1]) ** 2)
                BP = math.sqrt((ponto_90[0] - ponto_B[0]) ** 2 + (ponto_90[1] - ponto_B[1]) ** 2)

                try:
                    #angulo_ABP = math.degrees(math.atan(AP / BP))
                    angulo_BAP = math.degrees(math.atan(BP / AP))

                except ZeroDivisionError:
                    angulo_BAP = 0

                angulos.append(angulo_BAP)
        else:
            print('Nenhuma faixa foi encontrada. Ajuste os parâmetros para identificá-las!')

        return pontos, angulos

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
        picos = signal.find_peaks_cwt(histograma, np.arange(1, 200), min_length=200)

        ponto_medio = int(histograma.shape[0] / 2)

        print('Qtd de picos:', len(picos))

        if len(picos) > 1:
            # Caso mais de dois picos sejam encontrados, selecionamos apenas o mais à esquerda e o mais à direita
            pico_esquerda, *_, pico_direita = picos

        # Caso contrário, escolhemos os pontos mais altos nas segmentações à esquerda e à direita do centro
        else:
            pico_esquerda = np.argmax(histograma[:ponto_medio])
            pico_direita = np.argmax(histograma[ponto_medio:]) + ponto_medio

        return pico_esquerda, pico_direita

# © 2023 CarAI.
