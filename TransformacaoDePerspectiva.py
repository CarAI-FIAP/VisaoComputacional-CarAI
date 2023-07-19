import cv2
import numpy as np

class TransformacaoDePerspectiva:
    # Classe para realizar transformações de perspectiva na imagem.

    def __init__(self):
        pass

    def calcular_params_para_transformar_perspectiva(self, img, centro_ajustavel_x=0):
        """
        Calcula os vértices da região de interesse e as matrizes necessárias.

        Parâmetro(s):
            img (np.array): Imagem que será processada.
            x_centro_ajustavel: Deslocamento ajustável do centro da imagem.

        Retorno(s):
            M (np.array): Matriz para transformar a imagem para a 'Bird's Eye View'.
            M_inv (np.array): Matriz para transformar a imagem da 'Bird's Eye View' para a normal.
        """
        img_altura = img.shape[0]
        img_largura = img.shape[1]

        # Calcula a posição horizontal do centro da imagem adicionando um deslocamento ajustável
        centro_x = img_largura / 2 + centro_ajustavel_x

        # Definição dos valores fixos para os deslocamentos e coordenadas dos pontos de origem
        xfd = 54        # Deslocamento horizontal em relação ao centro da imagem
        yf = 450        # Posição vertical dos pontos de origem
        offset_x = 120   # Deslocamento horizontal dos pontos de origem em relação às bordas da imagem

        # Coordenadas dos 4 pontos de origem
        src = np.float32([(offset_x, img_altura),                # top-left
                         (centro_x - xfd, yf),                   # bottom-left
                         (centro_x + xfd, yf),                   # bottom-right
                         (img_largura - offset_x, img_altura)])  # top-right

        # Coordenadas dos 4 pontos de destino
        dst = np.float32([(offset_x, img_largura),
                         (offset_x, 0),
                         (img_altura - offset_x, 0),
                         (img_altura - offset_x, img_largura)])

        M = cv2.getPerspectiveTransform(src, dst)
        M_inv = cv2.getPerspectiveTransform(dst, src)

        return M, M_inv

    def mudar_perspectiva(self, img):
        """
        Realiza a transformação da perspectiva da imagem para a 'Bird's Eye View'.

        Parâmetro(s):
            img (np.array): Imagem que será processada.

        Retorno(s):
            img (np.array): Imagem em perspectiva superior.
        """
        M, _ = self.calcular_params_para_transformar_perspectiva(img)

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

        _, M_inv = self.calcular_params_para_transformar_perspectiva(img)

        img_dimensoes = (img.shape[0], img.shape[1])

        return cv2.warpPerspective(img, M_inv, img_dimensoes, flags=cv2.INTER_LINEAR)

# © 2023 CarAI.
