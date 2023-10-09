import sys
import cv2
import math
import matplotlib.pyplot as plt
from mpi4py import MPI
import serial
import time

from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *
from Configuracoes import *
from PainelDeControle import *

configuracoes = Configuracoes()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

comunicacao_arduino_on = True

if comunicacao_arduino_on:
    if rank == 0:
        port = 'COM15'  # 15
        rate = 9600

        serial_arduino = serial.Serial(port, rate, timeout=0.1)

ativar_deteccao_faixas = True
ativar_deteccao_objetos = True
ativar_painel_de_controle = False

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
        self.angulo_offset = 2000
        self.placa_pare = 0
        self.semaforo = 0

        self.dados = []

    def fechar_conexao_arduino(self):
        serial_arduino.close()

    def enviar_dados_para_arduino(self, dados, debug=True):
        angulo, angulo_ffset, offset, esquerda_x, direita_x, placa_pare, semaforo = dados
        valor_descartavel = 0

        dados_enviar = f'{angulo},{angulo_ffset},{offset},{esquerda_x},{direita_x},{valor_descartavel},{placa_pare},{semaforo}\n'

        serial_arduino.write(dados_enviar.encode())
        time.sleep(0.01)

        if debug:
            dados_recebidos = serial_arduino.readline().decode('utf-8').strip()
            print(f'\n{dados_recebidos}', end='')

    def configurar_captura_de_imagem(self, camera_on, caminho_camera, caminho_video=''):
        if camera_on:
            video = cv2.VideoCapture(caminho_camera, cv2.CAP_DSHOW)

            video.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_largura)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_altura)
            video.set(cv2.CAP_PROP_FPS, 30)
            video.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video = cv2.VideoCapture(caminho_video)

        return video

    def processar_videos(self, caminho_video_faixas='', caminho_video_sinalizacao=''):
        video_faixas = self.configurar_captura_de_imagem(self.camera_faixas_on, -0, caminho_video_faixas)
        video_sinalizacao = self.configurar_captura_de_imagem(self.camera_sinalizacao_on, 1, caminho_video_sinalizacao)

        while video_faixas.isOpened() or video_sinalizacao.isOpened():
            video_faixas_nao_acabou, frame_faixas = video_faixas.read()
            video_sinalizacao_nao_acabou, frame_sinalizacao = video_sinalizacao.read()

            if video_faixas_nao_acabou or video_sinalizacao_nao_acabou:
                frame_faixas_reduzido = self.tratamento.redimensionar_por_fator(frame_faixas, self.configuracoes.fator_reducao)
                frame_sinalizacao_reduzido = self.tratamento.redimensionar_por_fator(frame_sinalizacao, self.configuracoes.fator_reducao)

                if ativar_deteccao_faixas:
                    self.angulo, self.angulo_offset, self.offset, self.esquerda_x, self.direita_x  = self.faixas.identificar_faixas(frame_faixas_reduzido)

                if ativar_deteccao_objetos:
                    self.placa_pare, self.semaforo = self.sinalizacao.classificar_objetos(frame_sinalizacao_reduzido)

            self.dados.append(self.angulo)
            self.dados.append(self.angulo_offset)
            self.dados.append(self.offset)
            self.dados.append(self.esquerda_x)
            self.dados.append(self.direita_x)
            self.dados.append(self.placa_pare)
            self.dados.append(self.semaforo)

            if len(self.dados) == 7:
                sys.stdout.flush()

                if comunicacao_arduino_on:
                    self.enviar_dados_para_arduino(self.dados)

                self.dados.clear()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.fechar_conexao_arduino()
                break

        video_faixas.release()
        video_sinalizacao.release()
        cv2.destroyAllWindows()

def main():
    processar_tudo = ativar_deteccao_faixas and ativar_deteccao_objetos and ativar_painel_de_controle

    if processar_tudo:
        if rank == 0:
            video_faixas = 'assets/videos_teste/pista_completa.mp4'
            video_objetos = 'assets/videos_teste/semaforo.mp4'

            visaoComputacional = VisaoComputacional()
            visaoComputacional.processar_videos(video_faixas, video_objetos)

            for i in range(1, comm.Get_size()):
                comm.send(None, dest=i, tag=1)

        elif ativar_painel_de_controle and rank == 1:
            configuracoes.inicializar_painel_de_controle()

    else:
        video_faixas = 'assets/videos_teste/pista_completa.mp4'
        video_objetos = 'assets/videos_teste/placa_pare1.mp4'

        visaoComputacional = VisaoComputacional()

        if not ativar_painel_de_controle:
            visaoComputacional.processar_videos(video_faixas, video_objetos)

        else:
            visaoComputacional.configuracoes.inicializar_painel_de_controle()

if __name__ == '__main__':
    main()

# © 2023 CarAI.
