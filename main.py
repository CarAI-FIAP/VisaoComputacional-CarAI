import cv2
import math
import matplotlib.pyplot as plt

from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *

class VisaoComputacional:
    # Classe contendo a implementação de todos os algoritmos de visão computacional do veículo

    def __init__(self):
        self.fator_reducao = 1

        self.tratamento = TratamentoDeImagem()
        self.faixas = FaixasDeTransito(self.fator_reducao)
        #self.sinalizacao = SinaisDeTransito() # Comentar p/ diminuir a demora na inicialização

    def processar_video(self, caminho_video, funcao):
        cap = cv2.VideoCapture(caminho_video)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        while cap.isOpened():
            video_nao_acabou, frame = cap.read()

            if video_nao_acabou:
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                funcao(frame_reduzido)

            #out_frame = funcao(frame)
            #cv2.imshow('Video', self.tratamento.redimensionar_imagem(out_frame, 350))

            if cv2.waitKey(10) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def processar_video_faixas(self, video):
        self.processar_video(video, self.faixas.identificar_faixas)

    def processar_video_sinalizacoes(self, video):
        self.processar_video(video, self.sinalizacao.classificar_objetos)

def main():
    video_faixas = 'assets/videos_teste/pista.mp4'

    #video_faixas = 'assets/videos_teste/pista.mp4'

    #video_objetos = 'assets/videos_teste/placa.mp4'

    camera_celular = 'https://172.16.53.24:8080/video'

    visaoComputacional = VisaoComputacional()
    visaoComputacional.processar_video_faixas(1)
    #visaoComputacional.processar_video_sinalizacoes(video_objetos)

if __name__ == '__main__':
    main()

# © 2023 CarAI.
