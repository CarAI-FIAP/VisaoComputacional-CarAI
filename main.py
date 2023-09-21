import sys
import cv2
import math
import matplotlib.pyplot as plt
from mpi4py import MPI

from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *
from Configuracoes import *
from PainelDeControle import *

configuracoes = Configuracoes()

comunicacao_arduino = False

port = 'COM9'
rate = 9600

if comunicacao_arduino:
    serial_arduino = serial.Serial(port, rate)

class VisaoComputacional:
    # Classe contendo a implementação de todos os algoritmos de visão computacional do veículo

    def __init__(self):
        self.configuracoes = Configuracoes()
        self.tratamento = TratamentoDeImagem()
        self.faixas = FaixasDeTransito()
        self.sinalizacao = SinaisDeTransito()  # Comentar p/ diminuir a demora na inicialização

        self.camera_faixas_on = False
        self.camera_sinalizacao_on = False
        self.video_largura = 1280
        self.video_altura = 720

        self.angulo = 1999
        self.esquerda_x = 0
        self.direita_x = 0
        self.offset = 2000
        self.placa_pare = 0
        self.semaforo = 0

        self.dados = []

    def fechar_conexao_arduino(self):
        serial_arduino.close()

    def enviar_dados_para_arduino(self, dados, debug=False):
        angulo, esquerda_x, direita_x, offset, placa_pare, semaforo = dados
        dados_enviar = f'{angulo},{esquerda_x},{direita_x},{offset},{placa_pare},{semaforo}\n'

        serial_arduino.write(dados_enviar.encode())
        time.sleep(0.01)

        if debug:
            dados_recebidos = serial_arduino.readline().decode('utf-8').strip()
            print(f'\n{dados_recebidos}', end='')

    def processar_videos(self, caminho_video_faixas='', caminho_video_sinalizacao=''):
        if self.camera_faixas_on:
            video_faixas = cv2.VideoCapture(-0, cv2.CAP_DSHOW)

            video_faixas.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            video_faixas.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            video_faixas.set(cv2.CAP_PROP_FPS, 30)
            video_faixas.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video_faixas = cv2.VideoCapture(caminho_video_faixas)

        if self.camera_sinalizacao_on:
            video_sinalizacao = cv2.VideoCapture(1, cv2.CAP_DSHOW)

            video_sinalizacao.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            video_sinalizacao.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            video_sinalizacao.set(cv2.CAP_PROP_FPS, 30)
            video_sinalizacao.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video_sinalizacao = cv2.VideoCapture(caminho_video_sinalizacao)

        while video_faixas.isOpened() or video_sinalizacao.isOpened():
            video_faixas_nao_acabou, frame_faixas = video_faixas.read()
            video_sinalizacao_nao_acabou, frame_sinalizacao = video_sinalizacao.read()

            if video_faixas_nao_acabou:
                frame_faixas_reduzido = self.tratamento.redimensionar_por_fator(frame_faixas, self.configuracoes.fator_reducao)

                self.angulo, self.esquerda_x, self.direita_x, self.offset = self.faixas.identificar_faixas(frame_faixas_reduzido)

            if video_sinalizacao_nao_acabou:
                frame_sinalizacao_reduzido = self.tratamento.redimensionar_por_fator(frame_sinalizacao, self.configuracoes.fator_reducao)

                self.placa_pare, self.semaforo = self.sinalizacao.classificar_objetos(frame_sinalizacao_reduzido)

            self.dados.append(self.angulo)
            self.dados.append(self.esquerda_x)
            self.dados.append(self.direita_x)
            self.dados.append(self.offset)
            self.dados.append(self.placa_pare)
            self.dados.append(self.semaforo)

            if len(self.dados) == 6:
                print(self.dados)
                sys.stdout.flush()

                if comunicacao_arduino:
                    self.enviar_dados_para_arduino(self.dados)

                self.dados.clear()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.fechar_conexao_arduino()
                break

        video_faixas.release()
        video_sinalizacao.release()
        cv2.destroyAllWindows()

def main():
    processar_tudo = True

    if processar_tudo:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()  # ID ou classificação única dentro do comunicador

        if rank == 0:
            # Processo mestre
            video_faixas = 'assets/videos_teste/pista_completa.mp4'
            video_objetos = 'assets/videos_teste/placa_pare1.mp4'

            visaoComputacional = VisaoComputacional()

            comm.bcast(video_faixas, root=0)
            comm.bcast(video_objetos, root=0)

            if rank == 0:
                visaoComputacional.processar_videos(video_faixas, video_objetos)

            # Espere que os processos filhos terminem
            for i in range(1, comm.Get_size()):
                comm.send(None, dest=i, tag=1)
        else:
            # Processos filhos
            if rank == 1:
                # Processo filho 1
                configuracoes.inicializar_painel_de_controle()

    else:
        video_faixas = 'assets/videos_teste/pista_completa.mp4'
        video_objetos = 'assets/videos_teste/placa_pare1.mp4'

        visaoComputacional = VisaoComputacional()
        visaoComputacional.processar_videos(video_faixas, video_objetos)

if __name__ == '__main__':
    main()

# © 2023 CarAI.
