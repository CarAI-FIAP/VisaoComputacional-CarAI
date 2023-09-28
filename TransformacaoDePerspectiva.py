import cv2
import numpy as np

from Configuracoes import *

class TransformacaoDePerspectiva:
    # Classe para realizar transformações de perspectiva na imagem.

    def __init__(self):
        #self.configuracoes = Configuracoes()
        self.fator_reducao = 3

        # Definição dos valores fixos para os deslocamentos e coordenadas dos pontos de origem
        self.xfd = (450 // self.fator_reducao)   # Deslocamento horizontal em relação ao centro da imagem
        self.yf = (450 // self.fator_reducao)     # Posição vertical dos pontos de origem
        self.offset_x = 0                                  # Deslocamento horizontal dos pontos de origem em relação às bordas da imagem

        self.perspectiva_retangular = False

    def desenhar_roi(self, img, cor_linha=(0, 255, 0), tam_linha=2):
        """
        Desenha um polígono delimitando a região de interesse na imagem.

        Parâmetro(s):
            img (np.array): Imagem de entrada.
            cor_linha (r, g, b): Cor do polígono da região de interesse.
            tam_linha (int): Espessura da linha do polígono.

        Retorno(s):
            img_roi (np.array): Imagem com polígono da região de interesse desenhado.
        """
        parametros = self.calcular_params_para_transformar_perspectiva(img)
        src = parametros[2]

        img_roi = np.zeros_like(img)
        cv2.fillPoly(img_roi, [np.int32(src)], (255, 0, 0))
        img_roi = cv2.bitwise_and(img, img_roi)

        return img_roi

    def calcular_params_para_transformar_perspectiva(self, img, centro_ajustavel_x=0):
        """
        Calcula os vértices da região de interesse e as matrizes necessárias.

        Parâmetro(s):
            img (np.array): Imagem que será processada.
            x_centro_ajustavel (int): Deslocamento ajustável do centro da imagem.

        Retorno(s):
            M (np.array): Matriz para transformar a imagem para a 'Bird's Eye View'.
            M_inv (np.array): Matriz para transformar a imagem da 'Bird's Eye View' para a normal.
            src (np.array): Coordenadas dos 4 pontos de origem.
            dst (np.array): Coordenadas dos 4 pontos de destino.
        """
        img_altura = img.shape[0]
        img_largura = img.shape[1]

        # Calcula a posição horizontal do centro da imagem adicionando um deslocamento ajustável
        centro_x = img_largura / 2 + centro_ajustavel_x

        #if not(self.birds_view):
            #self.xfd = img.shape[1]

        if self.perspectiva_retangular:
            src = np.float32([
                (self.offset_x, img_altura),  # top-left
                (self.offset_x, self.yf),  # bottom-left
                (img_largura - self.offset_x, self.yf),  # bottom-right
                (img_largura - self.offset_x, img_altura)  # top-right
            ])

        else:
            src = np.float32([(self.offset_x, img_altura),                      # top-left
                               (centro_x - self.xfd, self.yf),              # bottom-left
                               (centro_x + self.xfd, self.yf),              # bottom-right
                               (img_largura - self.offset_x, img_altura)])  # top-right

        dst = np.float32([(self.offset_x, img_largura),
                               (self.offset_x, 0),
                               (img_altura - self.offset_x, 0),
                               (img_altura - self.offset_x, img_largura)])

        M = cv2.getPerspectiveTransform(src, dst)
        M_inv = cv2.getPerspectiveTransform(dst, src)

        return M, M_inv, src, dst

    def mudar_perspectiva(self, img):
        """
        Realiza a transformação da perspectiva da imagem para a 'Bird's Eye View'.

        Parâmetro(s):
            img (np.array): Imagem que será processada.

        Retorno(s):
            img (np.array): Imagem em perspectiva superior.
        """
        parametros = self.calcular_params_para_transformar_perspectiva(img)
        M = parametros[0]

        dimensoes_img = (img.shape[0], img.shape[1])

        return cv2.warpPerspective(img, M, dimensoes_img, flags=cv2.INTER_LINEAR)

    def resetar_perspectiva(self, img):
        """
        Realiza a transformação da perspectiva da imagem para a visão frontal (original).

        Parâmetro(s):
            img (np.array): Imagem em perspectiva superior.

        Retorno(s):
            img (np.array): Imagem frontal.
        """
        parametros = self.calcular_params_para_transformar_perspectiva(img)
        M_inv = parametros[1]

        img_dimensoes = (img.shape[0], img.shape[1])

        return cv2.warpPerspective(img, M_inv, img_dimensoes, flags=cv2.INTER_LINEAR)

# © 2023 CarAI.
