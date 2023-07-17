import cv2
import numpy as np

class TratamentoDeImagem:
    # Classe para reunir todos os métodos de tratamento de imagem.

    def __init__(self):
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
        canal_h = hls[:,:,0]
        canal_l = hls[:,:,1]
        canal_s = hls[:,:,2]
        canal_v = hsv[:,:,2]

        faixa_direita = self.threshold_relativo(canal_l, 0.85, 1.0)
        #faixa_direita[:,:750] = 0

        faixa_esquerda = self.threshold_absoluto(canal_h, 20, 30)
        faixa_esquerda &= self.threshold_relativo(canal_v, 0.85, 1.0)
        #faixa_esquerda[:,550:] = 0

        img_binarizada = faixa_esquerda | faixa_direita

        return img_binarizada

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
        img_altura = img.shape[0]
        img_largura = img.shape[1]

        xfd = 120
        yf = 450
        offset_x = 120

        centro_x = img_largura // 2

        pontos_roi = np.array([(offset_x, img_altura),                 # top-left
                               (centro_x - xfd, yf),                   # bottom-left
                               (centro_x + xfd, yf),                   # bottom-right
                               (img_largura - offset_x, img_altura)])  # top-right

        img_roi = np.zeros_like(img)
        cv2.fillPoly(img_roi, [pontos_roi], (255, 0, 0))
        img_roi = cv2.bitwise_and(img, img_roi)

        return img_roi