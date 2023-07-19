import cv2
import math

import matplotlib.pyplot as plt

from CalibracaoCamera import CalibracaoCamera
from TratamentoDeImagem import *
from TransformacaoDePerspectiva import *
from FaixasDeTransito import *

class IdentificaFaixasDeTransito:
    # Classe para identificar as faixas da pista

    def __init__(self):
        self.calibracao = CalibracaoCamera('camera_cal', 9, 6)
        self.tratamento = TratamentoDeImagem()
        self.transformacao = TransformacaoDePerspectiva()
        self.faixas = FaixasDeTransito()

    def identificar_faixas(self, img):
        #out_img = np.copy(img)

        #img = self.calibracao.corrigir_distorcao(img)
        img_warped = self.transformacao.mudar_perspectiva(img)
        img_threshold = self.tratamento.binarizar_imagem(img_warped)
        img_filtrada = self.tratamento.aplicar_filtros(img_threshold)
        #img_roi = self.tratamento.desenhar_roi(img_filtrada)

        pontos, angulo = self.faixas.calcular_resultados_faixas(img_filtrada, 1100)
        out_img = self.faixas.plotar_resultados(img_warped, pontos, angulo)

        cv2.imshow('img_filtrada', self.tratamento.redimensionar_imagem(img_filtrada, 350))
        cv2.imshow('img', self.tratamento.redimensionar_imagem(img, 350))

        return out_img

    def processar_video(self, input_path):
        cap = cv2.VideoCapture(input_path)

        while cap.isOpened():
            _, frame = cap.read()

            out_frame = self.identificar_faixas(frame)

            cv2.imshow('Video', self.tratamento.redimensionar_imagem(out_frame, 350))

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

class IdentificaSinalizacoes:
    # Classe para identificar e classificar sinais de trânsito e semáforos

    def __init__(self):
        pass

def main():
    identificaFaixas = IdentificaFaixasDeTransito()
    identificaFaixas.processar_video('assets/videos_teste/pista.mp4')

if __name__ == "__main__":
    main()

# © 2023 CarAI.
