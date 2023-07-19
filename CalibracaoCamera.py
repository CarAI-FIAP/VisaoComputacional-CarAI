import numpy as np
import cv2
import glob
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

class CalibracaoCamera():
    """
    Classe que realiza a calibração da câmera usando imagens de tabuleiro de xadrez.

    Atributos:
        mtx (np.array): Matriz da câmera
        dist (np.array): Coeficientes de distorção
    """

    def __init__(self, imgs_dir, nx, ny, debug=False):
        """
        Inicialização da classe CalibracaoCamera.

        Parâmetros:
            imgs_dir (str): Caminho para o diretório que contém as imagens de tabuleiro de xadrez.
            nx (int): Largura do tabuleiro de xadrez (número de quadrados).
            ny (int): Altura do tabuleiro de xadrez (número de quadrados).
        """
        nomes_arquivos = glob.glob("{}/*".format(imgs_dir))
        pontos_objeto = []
        pontos_imagem = []
        
        # Coordenadas dos cantos do tabuleiro de xadrez em 3D
        objp = np.zeros((nx*ny, 3), np.float32)
        objp[:,:2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)
        
        # Percorre todas as imagens de tabuleiro de xadrez
        for nome_arquivo in nomes_arquivos:
            img = mpimg.imread(nome_arquivo)

            # Converte a imagem para escala de cinza
            img_cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            # Encontra os cantos do tabuleiro de xadrez
            ret, cantos = cv2.findChessboardCorners(img_cinza, (nx, ny))
            if ret:
                pontos_imagem.append(cantos)
                pontos_objeto.append(objp)

        img_dimensoes = (img.shape[1], img.shape[0])
        ret, self.mtx, self.dist, _, _ = cv2.calibrateCamera(pontos_objeto, pontos_imagem, img_dimensoes, None, None)

        if not ret:
            raise Exception("Não foi possível calibrar a câmera")

    def corrigir_distorcao(self, img):
        """
        Retorna a imagem sem distorções.

        Parâmetro(s):
            img (np.array): Imagem de entrada.

        Retorno(s):
            Imagem (np.array): Imagem corrigida de distorção.
        """

        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx)

# © 2023 CarAI.
