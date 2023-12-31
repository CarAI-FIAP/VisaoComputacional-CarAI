import cv2
import numpy as np

from Configuracoes import *

dark_mode = False

class TratamentoDeImagem:
    # Classe para reunir todos os métodos de tratamento de imagem.

    def __init__(self):
        #self.configuracoes = Configuracoes()
        pass

    def aplicar_filtros(self, img):
        """
        Aplica uma sequência de operações morfológicas para filtrar ruídos causados por luzes.

        Parâmetro(s):
            img (np.array): Imagem de entrada.

        Retorno(s):
            img filtrada (np.array): Imagem filtrada.
        """

        img_fechamento = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)
        img_abertura = cv2.morphologyEx(img_fechamento, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
        img_dilatacao = cv2.dilate(img_abertura, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)

        return img_dilatacao

    def juntar_videos(self, imgs):
        for i in range(0, len(imgs)):
            if len(imgs[i].shape) == 2:
                imgs[i] = cv2.cvtColor(imgs[i], cv2.COLOR_GRAY2BGR)

        return np.hstack(imgs)

    def threshold_relativo(self, img, limite_inf, limite_sup):
        """
        Aplica o threshold relativo aos valores máximos da imagem para extrair pixels relevantes.

        Parâmetro(s):
            img (np.array): Imagem de entrada.
            limite_inf (float): Limite inferior para o threshold relativo, varia de 0 a 1.
            limite_sup (float): Limite superior para o threshold relativo, varia de 0 a 1.

        Retorno(s):
            img binária (np.array): Imagem binária onde os pixels relevantes possuem o valor 255 (branco) e os demais o valor 0 (preto).
        """
        valor_min = np.min(img)
        valor_max = np.max(img)

        limite_inf_real = valor_min + (valor_max - valor_min) * limite_inf
        limite_sup_real = valor_min + (valor_max - valor_min) * limite_sup

        return np.uint8((img >= limite_inf_real) & (img <= limite_sup_real)) * 255

    def threshold_absoluto(self, img, limite_inf, limite_sup):
        """
        Aplica o threshold absoluto sem considerar os valores máximos da imagem para extrair pixels relevantes.

        Parâmetro(s):
            img (np.array): Imagem de entrada.
            limite_inf (float): Limite inferior para o threshold.
            limite_sup (float): Limite superior para o threshold.

        Retorno(s):
            img binária (np.array): Imagem binária onde os pixels relevantes possuem o valor 255 (branco) e os demais o valor 0 (preto).
        """
        return np.uint8((img >= limite_inf) & (img <= limite_sup)) * 255

    def binarizar_imagem(self, img):
        """
        Aplica os métodos de threshold e binariza imagem e deixar apenas as faixas da pista em branco.

        Parâmetro(s):
            img (np.array): Imagem de entrada.

        Retorno(s):
            img binária (np.array): Imagem binária onde os pixels relevantes possuem o valor 255 (branco) e os demais o valor 0 (preto).
        """
        # Converte a imagem de RGB para o espaço de cores HLS e HSV e separa as imagens para cada canal.
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        canal_h = hls[:,:,0]
        canal_l = hls[:,:,1]
        canal_s = hls[:,:,2]
        canal_v = hsv[:,:,2]
        canal_b = bgr[:,:,0]
        canal_g = bgr[:,:,1]
        canal_r = bgr[:,:,2]

        if dark_mode:
            faixa_direita = self.threshold_relativo(canal_l, 0.4, 1.0) # 0.78
            #faixa_direita = cv2.threshold(canal_l, (120, 255), cv2.THRESH_BINARY)
            #faixa_direita = cv2.GaussianBlur(faixa_direita, (3, 3))
            faixa_direita &= self.threshold_absoluto(canal_s, 70, 255) # 40
            faixa_direita &= self.threshold_absoluto(canal_s, 70, 255) # 40
            #faixa_direita &= self.threshold_relativo(canal_v, 0.85, 1.0)
            #faixa_direita[:,:750] = 0

            faixa_esquerda = self.threshold_absoluto(canal_h, 15, 30)
            faixa_esquerda = self.threshold_relativo(canal_g, 0.2, 1.0)
            faixa_esquerda = self.threshold_relativo(canal_r, 0.1, 1.0)
            #faixa_esquerda &= self.threshold_absoluto(canal_s, 30, 255)
            faixa_esquerda &= self.threshold_relativo(canal_v, 0.7, 1.0)
            #faixa_esquerda[:,550:] = 0

        else:
            faixa_direita = self.threshold_relativo(canal_l, 0.85, 1.0) # 0.78
            #faixa_direita = cv2.threshold(canal_l, (120, 255), cv2.THRESH_BINARY)
            #faixa_direita = cv2.GaussianBlur(faixa_direita, (3, 3))
            #faixa_direita &= self.threshold_absoluto(canal_s, 50, 255) # 40
            #faixa_direita &= self.threshold_relativo(canal_v, 0.85, 1.0)
            #faixa_direita[:,:750] = 0

            faixa_esquerda = self.threshold_absoluto(canal_h, 20, 30)
            #faixa_esquerda &= self.threshold_absoluto(canal_s, 30, 255)
            faixa_esquerda &= self.threshold_relativo(canal_v, 0.95, 1.0)
            #faixa_esquerda[:,550:] = 0

        img_binarizada = faixa_esquerda | faixa_direita

        return img_binarizada

    def redimensionar_imagem(self, img, altura_desejada):
        """
        Redimensiona a imagem para uma altura desejada, mantendo a proporção original.

        Parâmetro(s):
            img (np.array): Imagem de entrada.
            altura_desejada (int): Altura desejada para a imagem redimensionada.

        Retorno:
            img_redimensionada (np.array): Imagem redimensionada.
        """
        ratio = altura_desejada / img.shape[0]
        dimensoes_img_redimensionada = (int(img.shape[1] * ratio), altura_desejada)

        return cv2.resize(img, dimensoes_img_redimensionada, interpolation=cv2.INTER_AREA)

    def redimensionar_por_fator(self, img, fator):
        largura = int(img.shape[1] / fator)
        altura = int(img.shape[0] / fator)

        return cv2.resize(img, (largura, altura))

    def aplicar_threshold(self, img, threshold_tipo=cv2.THRESH_BINARY + cv2.THRESH_OTSU):
        img_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_cinza, (5, 5), 1)

        return cv2.threshold(img_blur, 112, 255, threshold_tipo)[1]

    def sobel(self, img, orientacao='x', kernel=3):
        if orientacao == 'x':
            sobel = cv2.Sobel(img, cv2.CV_64F, 1, 0, kernel)

        if orientacao == 'y':
            sobel = cv2.Sobel(img, cv2.CV_64F, 0, 1, kernel)

        return sobel

    def aplicar_threshold_sobel(self, img, kernel, thresh=(0, 255)):
        sobelx = np.absolute(self.sobel(img, orientacao='x', kernel=kernel))

        # Get the magnitude of the edges that are horizontally aligned on the image
        sobely = np.absolute(self.sobel(img, orientacao='y', kernel=kernel))

        mag = np.sqrt(sobelx ** 2 + sobely ** 2)

        return mag

# © 2023 CarAI.
