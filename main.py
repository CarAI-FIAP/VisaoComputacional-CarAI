import sys
import cv2
import math
import matplotlib.pyplot as plt
from mpi4py import MPI

from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *

class VisaoComputacional:
    # Classe contendo a implementação de todos os algoritmos de visão computacional do veículo

    def __init__(self):
        #self.configuracoes = Configuracoes()

        self.camera_faixas_on = False
        self.camera_sinalizacao_on = False
        self.video_largura = 1280
        self.video_altura = 720

        self.fator_reducao = 3

        self.tratamento = TratamentoDeImagem()
        self.faixas = FaixasDeTransito()
        self.sinalizacao = SinaisDeTransito()  # Comentar p/ diminuir a demora na inicialização

    def processar_video_faixas(self, caminho_video=''):
        if self.camera_faixas_on:
            video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
  
            video.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            video.set(cv2.CAP_PROP_FPS, 30)
            video.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video = cv2.VideoCapture(caminho_video)

        while video.isOpened():
            video_nao_acabou, frame = video.read()

            if video_nao_acabou:
                #print(self.configuracoes.canal_l_min.get())
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                self.faixas.identificar_faixas(frame_reduzido)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.faixas.fechar_conexao()
                break

        video.release()
        cv2.destroyAllWindows()

    def processar_video_sinalizacoes(self, caminho_video=''):
        if self.camera_sinalizacao_on:
            video = cv2.VideoCapture(-0, cv2.CAP_DSHOW)

            video.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            video.set(cv2.CAP_PROP_FPS, 30)
            video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video = cv2.VideoCapture(caminho_video)

        while video.isOpened():
            video_nao_acabou, frame = video.read()

            if video_nao_acabou:
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                self.sinalizacao.classificar_objetos(frame_reduzido)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.faixas.fechar_conexao()
                break

        video.release()
        cv2.destroyAllWindows()

def main():
    processar_tudo = False

    if processar_tudo:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()  # ID ou classificação única dentro do comunicador

        if rank == 0:
            # Processo mestre
            video_faixas = 'assets/videos_teste/pista_completa.mp4'
            video_objetos = 'assets/videos_teste/semaforo_vermelho.mp4'

            visaoComputacional = VisaoComputacional()

            # Divida o trabalho entre os processos
            comm.bcast(video_faixas, root=0)
            comm.bcast(video_objetos, root=0)

            # Inicialize o painel de controle em um processo separado
            # if rank == 0:
            # painelDeControle = PainelDeControle()
            # painelDeControle.mainloop()

            # Espere que os processos filhos terminem
            for i in range(1, comm.Get_size()):
                comm.send(None, dest=i, tag=1)
        else:
            # Processos filhos
            video_faixas = comm.bcast(None, root=0)
            video_objetos = comm.bcast(None, root=0)  # Receba o caminho do vídeo de objetos

            if rank == 1:
                # Processo filho 1: processar_video_sinalizacoes
                visaoComputacional = VisaoComputacional()
                visaoComputacional.processar_video_faixas(video_faixas)

            # elif rank == 2:
            # Processo filho 2: processar_video_faixas
            #    visaoComputacional = VisaoComputacional()
            #    visaoComputacional.processar_video_sinalizacoes(video_objetos)

    else:
        video_faixas = 'assets/videos_teste/pista_completa.mp4'

        video_objetos = 'assets/videos_teste/placa_pare1.mp4'

        visaoComputacional = VisaoComputacional()
        visaoComputacional.processar_video_faixas(video_faixas)
        # visaoComputacional.processar_video_sinalizacoes(video_objetos)

        # painelDeControle = PainelDeControle()
        # painelDeControle.mainloop()

if __name__ == '__main__':
    main()

# © 2023 CarAI.
