import cv2
import math
import matplotlib.pyplot as plt

from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *

print(cv2.__version__)

class VisaoComputacional:
    # Classe contendo a implementação de todos os algoritmos de visão computacional do veículo

    def __init__(self):
        self.fator_reducao = 4
        self.camera_on = False
        self.video_largura = 1280
        self.video_altura = 720

        self.tratamento = TratamentoDeImagem()
        self.faixas = FaixasDeTransito(self.fator_reducao)
        #self.sinalizacao = SinaisDeTransito() # Comentar p/ diminuir a demora na inicialização

    def processar_video(self, funcao, caminho_video=''):
        if self.camera_on:
            cap = cv2.VideoCapture(-0, cv2.CAP_DSHOW)

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            cap = cv2.VideoCapture(caminho_video)

        while cap.isOpened():
            video_nao_acabou, frame = cap.read()

            if video_nao_acabou:
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                funcao(frame_reduzido)

            #out_frame = funcao(frame)
            #cv2.imshow('Video', self.tratamento.redimensionar_imagem(out_frame, 350))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def processar_video_faixas(self, video=''):
        self.processar_video(self.faixas.identificar_faixas, video)

    def processar_video_sinalizacoes(self, video=''):
        self.processar_video(self.sinalizacao.classificar_objetos, video)

def main():
    video_faixas = 'assets/videos_teste/pista_completa.mp4'

    #video_objetos = 'assets/videos_teste/placa.mp4'

    visaoComputacional = VisaoComputacional()
    visaoComputacional.processar_video_faixas(video_faixas)
    #visaoComputacional.processar_video_sinalizacoes(video_objetos)

if __name__ == '__main__':
    main()

# © 2023 CarAI.
