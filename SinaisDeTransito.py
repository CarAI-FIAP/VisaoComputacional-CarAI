import cv2
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO
from ultralytics import NAS
import serial
import time

from TratamentoDeImagem import *

# Carregamento do modelo
modelo_yolo = YOLO('models/yolov8m.pt')
#modelo_yolo = NAS('yolo_nas_s.pt')

class SinaisDeTransito:
    # Classe para identificar as placas de trânsito e os semáforos.

    def __init__(self):
        self.tratamento = TratamentoDeImagem()

        self.semaforo = 0
        self.placa_pare = 0

        self.tempo_placa_pare_detectada = None
        self.tempo_de_parada = 5
        self.intervalo_deteccao_placa_pare = self.tempo_de_parada + 20

    def classificar_objetos(self, img, debug=True):
        # Roda o modelo YOLOv8 treinado na imagem
        resultados = modelo_yolo(img, verbose=False, classes=[9, 11])

        for resultado in resultados:
            boxes = resultado.boxes.cpu().numpy()

            for box in boxes:
                label_identificado = int(box.cls[0])

                # label 11 = stop sign | 9 = traffic light
                if label_identificado == 11:
                    x1, y1, x2, y2 = box.xyxy[0] # Coordenadas do retângulo da placa detectada

                    placa = img[int(y1):int(y2), int(x1):int(x2)]  # Recorta a região da placa

                    # Converter a imagem para o espaço de cores HSV
                    hsv_placa = cv2.cvtColor(placa, cv2.COLOR_BGR2HSV)

                    # Definir os intervalos de cor para o vermelho em HSV
                    lower_red = np.array([0, 100, 100])
                    upper_red = np.array([10, 255, 255])
                    mask_red1 = cv2.inRange(hsv_placa, lower_red, upper_red)

                    lower_red = np.array([160, 100, 100])
                    upper_red = np.array([180, 255, 255])
                    mask_red2 = cv2.inRange(hsv_placa, lower_red, upper_red)

                    # Unir as máscaras para identificar os pixels vermelhos
                    mask_red = mask_red1 + mask_red2

                    total_pixels = placa.shape[0] * placa.shape[1]

                    # Calcular a porcentagem de pixels vermelhos na placa para saber se ela está de frente
                    porcentagem_vermelho = int((np.count_nonzero(mask_red) / total_pixels) * 100)
                    raio_placa = int((x2 - x1) / 2)

                    if debug:
                        print('\nStatus da placa pare:', self.placa_pare, ' | Raio: ', raio_placa, '| Pixels vermelhos na img (%):', porcentagem_vermelho)

                    # Verificar se a placa está próxima e de frente
                    if raio_placa >= 25 and porcentagem_vermelho > 25:
                        if self.tempo_placa_pare_detectada is None:
                            self.tempo_placa_pare_detectada = time.time()
                            self.placa_pare = 1

                        else:
                            tempo_atual = time.time()
                            tempo_decorrido = tempo_atual - self.tempo_placa_pare_detectada

                            if tempo_decorrido >= self.tempo_de_parada:
                                self.placa_pare = 0

                                if tempo_decorrido >= self.intervalo_deteccao_placa_pare:
                                    self.tempo_placa_pare_detectada = None

                    else:
                        self.placa_pare = 0

                if label_identificado == 9:
                    x1, y1, x2, y2 = box.xyxy[0]  # Coordenadas do retângulo do semáforo detectado
                    semaforo_identificado = img[int(y1):int(y2), int(x1):int(x2)]  # Recorta a região do semáforo

                    largura_semaforo = x2 - x1
                    #print(largura_semaforo)

                    # Dividir a imagem em três partes, uma para cada luz
                    luzes_semaforo = np.array_split(semaforo_identificado, 3)

                    # Calcular a quantidade de pixels de cada parte
                    luz_semaforo_qtd_pixels = [np.sum(cv2.cvtColor(luz_semaforo, cv2.COLOR_BGR2GRAY)) for luz_semaforo in luzes_semaforo]

                    # Classificação da cor do semáforo -> luz acesa possui mais pixels
                    luz_acesa = np.argmax(luz_semaforo_qtd_pixels) # Retorna o índice do maior valor do array
                    cores = ['vermelho', 'amarelo', 'verde']

                    if largura_semaforo > 25:
                        self.semaforo = luz_acesa + 1
                    else:
                        self.semaforo = 0

                    if debug:
                        print('\nStatus do semáforo:', self.semaforo, '|', 'Semáforo', cores[luz_acesa])

        img_com_resultados = resultados[0].plot()

        cv2.imshow('YOLO', self.tratamento.redimensionar_imagem(img_com_resultados, 450))

        return self.placa_pare, self.semaforo

# © 2023 CarAI.
