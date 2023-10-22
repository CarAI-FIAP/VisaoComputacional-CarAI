import sys
import cv2
import math
import os
import matplotlib.pyplot as plt
import multiprocessing
import threading

from PainelDeControle import *
from TratamentoDeImagem import *
from FaixasDeTransito import *
from SinaisDeTransito import *

comunicacao_arduino_on = False

ativar_deteccao_faixas = True
ativar_deteccao_objetos = True
ativar_painel_de_controle = False

serial_arduino = None

class VisaoComputacional:
    # Classe contendo a implementação de todos os algoritmos de visão computacional do veículo

    def __init__(self):
        # self.configuracoes = Configuracoes()

        self.camera_faixas_on = True
        self.camera_sinalizacao_on = True

        self.fator_reducao = 3

        self.tratamento = TratamentoDeImagem()
        self.faixas = FaixasDeTransito()
        self.sinalizacao = SinaisDeTransito()  # Comentar p/ diminuir a demora na inicialização

    def enviar_dados_para_arduino(self, dados_na_fila, debug=True):
        global serial_arduino

        if serial_arduino is None:
            port = 'COM4'  # 15
            rate = 9600

            serial_arduino = serial.Serial(port, rate, timeout=0.1)

        while True:
            if not dados_na_fila.empty():
                dados = dados_na_fila.get()

                serial_arduino.write(dados.encode())
                time.sleep(0.01)

                if debug:
                    dados_recebidos = serial_arduino.readline().decode().strip()
                    print(f'\n{dados_recebidos}', end='')

                    #sys.stdout.flush()

    #def fechar_conexao_arduino(self):
        #serial_arduino.close()

    def configurar_captura_de_imagem(self, camera_on, caminho_camera, caminho_video='', video_largura=1280, video_altura=720):
        if camera_on:
            video = cv2.VideoCapture(caminho_camera, cv2.CAP_DSHOW)

            video.set(cv2.CAP_PROP_FRAME_WIDTH, video_largura)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, video_altura)
            video.set(cv2.CAP_PROP_FPS, 30)
            video.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            video.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        else:
            video = cv2.VideoCapture(caminho_video)

        return video

    def processar_video_faixas(self, caminho_video='', dados_na_fila=None):
        video = self.configurar_captura_de_imagem(self.camera_faixas_on, 1, caminho_video)

        while video.isOpened():
            video_nao_acabou, frame = video.read()

            if video_nao_acabou:
                # print(self.configuracoes.canal_l_min.get())
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                angulo, angulo_offset, offset, faixa_esquerda, faixa_direita = self.faixas.identificar_faixas(
                    frame_reduzido)
                valor_descartavel = 0

                dados_faixas = f'A{angulo},{angulo_offset},{offset},{faixa_esquerda},{faixa_direita},{valor_descartavel}\n'

                if comunicacao_arduino_on:
                    if dados_na_fila:
                        dados_na_fila.put(dados_faixas)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.fechar_conexao_arduino()
                break

        video.release()
        cv2.destroyAllWindows()

    def processar_video_sinalizacoes(self, caminho_video='', dados_na_fila=None):
        video = self.configurar_captura_de_imagem(self.camera_sinalizacao_on, -0, caminho_video)

        while video.isOpened():
            video_nao_acabou, frame = video.read()

            if video_nao_acabou:
                frame_reduzido = self.tratamento.redimensionar_por_fator(frame, self.fator_reducao)

                placa_pare, semaforo = self.sinalizacao.classificar_objetos(frame_reduzido)
                valor_descartavel = 0

                dados_sinalizacao = f'B{valor_descartavel}{placa_pare},{semaforo}\n'
                #print(dados_sinalizacao)

                if comunicacao_arduino_on:
                    if dados_na_fila:
                        dados_na_fila.put(dados_sinalizacao)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.fechar_conexao_arduino()
                break

        video.release()
        cv2.destroyAllWindows()


def main():
    condicoes_de_processamento = [ativar_deteccao_faixas, ativar_deteccao_objetos, ativar_painel_de_controle]
    processar_tudo = sum(condicoes_de_processamento) >= 2

    visaoComputacional = VisaoComputacional()

    dados_na_fila_de_envio_do_arduino = multiprocessing.Queue()

    if comunicacao_arduino_on:
        thread_enviar_dados_para_arduino = threading.Thread(
            target=visaoComputacional.enviar_dados_para_arduino,
            args=(dados_na_fila_de_envio_do_arduino,)
        )
        thread_enviar_dados_para_arduino.start()

    if processar_tudo:
        if ativar_deteccao_faixas:
            video_faixas = 'assets/videos_teste/pista_completa.mp4'
            processo_video_faixas = multiprocessing.Process(
                target=visaoComputacional.processar_video_faixas,
                args=(video_faixas, dados_na_fila_de_envio_do_arduino,)
            )
            processo_video_faixas.start()

        if ativar_deteccao_objetos:
            video_objetos = 'assets/videos_teste/semaforo.mp4'
            processo_video_sinalizacoes = multiprocessing.Process(
                target=visaoComputacional.processar_video_sinalizacoes,
                args=(video_objetos, dados_na_fila_de_envio_do_arduino,)
            )
            processo_video_sinalizacoes.start()
            processo_video_sinalizacoes.join()
            processo_video_sinalizacoes.terminate()

        if ativar_painel_de_controle:
            painelDeControle = PainelDeControle()

            processo_inicializar_painel_de_controle = multiprocessing.Process(
                target=painelDeControle.mainloop()
            )
            processo_inicializar_painel_de_controle.start()
            processo_inicializar_painel_de_controle.join()

    else:
        visaoComputacional = VisaoComputacional()

        if ativar_deteccao_faixas:
            video_faixas = 'assets/videos_teste/pista_completa.mp4'
            visaoComputacional.processar_video_faixas(video_faixas)

        elif ativar_deteccao_objetos:
            video_objetos = 'assets/videos_teste/semaforo.mp4'
            visaoComputacional.processar_video_sinalizacoes(video_objetos)

        elif ativar_painel_de_controle:
            painelDeControle = PainelDeControle()
            painelDeControle.mainloop()


if __name__ == '__main__':
    main()

# © 2023 CarAI.
