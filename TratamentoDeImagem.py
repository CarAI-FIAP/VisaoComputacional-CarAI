import cv2
import numpy as np
class TratamentoDeImagem:
    # Classe para reunir todos os métodos de tratamento de imagem.

    def __init__(self):
        self.nome_trackbar = 'Visao Computacional - Threshold'
        self.thresh = 115

        self.nome_thresh = 'Thresh'

        #self.criar_trackbar()

    def criar_trackbar(self):
        cv2.namedWindow(self.nome_trackbar)
        cv2.createTrackbar(self.nome_thresh, self.nome_trackbar, self.thresh, 255, self.atualizar_posicao_trackbar)

    def atualizar_posicao_trackbar(self, x):
        cv2.getTrackbarPos(self.nome_thresh, self.nome_trackbar)
        print(self.thresh)

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
        canal_r = bgr[:,:,2]

        faixa_direita = self.threshold_relativo(canal_l, 0.9, 1.0)
        #faixa_direita &= self.threshold_absoluto(canal_s, 30, 255)
        #faixa_direita &= self.threshold_relativo(canal_v, 0.85, 1.0)
        #faixa_direita[:,:750] = 0

        faixa_esquerda = self.threshold_absoluto(canal_h, 20, 30)
        #faixa_esquerda &= self.threshold_absoluto(canal_s, 30, 255)
        faixa_esquerda &= self.threshold_relativo(canal_v, 0.85, 1.0)
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

    def aplicar_threshold(self, img, threshold_tipo=cv2.THRESH_BINARY_INV):
        img_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_cinza, (5, 5), 1)

        return cv2.threshold(img_blur, self.thresh, 255, threshold_tipo)[1]

# © 2023 CarAI.
