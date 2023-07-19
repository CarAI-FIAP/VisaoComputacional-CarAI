import cv2
import numpy as np
from ultralytics import YOLO

# Carregamento do modelo
model = YOLO('models/yolov8x.pt')

# Leitura do vídeo
video_path = 'assets/videos_teste/semaforo.mp4'
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    has_frame, frame = cap.read()

    if has_frame:
        # Roda o modelo YOLOv8 treinado no frame
        results = model(frame)

        for result in results:
            boxes = result.boxes.cpu().numpy()

            for box in boxes:
                key = int(box.cls[0])

                # key 11 = stop sign | 9 = traffic light
                if key == 11:
                    print('Pare!')

                if key == 9:
                    x1, y1, x2, y2 = box.xyxy[0]  # Coordenadas do retângulo do semáforo detectado
                    traffic_light_cropped_img = frame[int(y1):int(y2), int(x1):int(x2)]  # Recorta a região do semáforo

                    cv2.imwrite('traffic_light_cropped_img.jpg', traffic_light_cropped_img)

                    # Dividir a imagem em três partes, uma para cada luz
                    parts = np.array_split(traffic_light_cropped_img, 3)

                    # Calcular a quantidade de pixels de cada parte
                    sum_pixels_lights = [np.sum(cv2.cvtColor(part, cv2.COLOR_BGR2GRAY)) for part in parts]

                    # Classificação da cor do semáforo -> luz acesa possui mais pixels
                    max_pixels_index = np.argmax(sum_pixels_lights) # Retorna o índice do maior valor do array
                    colors = ['vermelho', 'amarelo', 'verde']
                    print('Semáforo', colors[max_pixels_index])

                # Visualizar os resultados no frame
                annotated_frame = results[0].plot()

                # Redimensionamento proporcional do vídeo para manter as proporções
                frame_height = 600
                ratio = frame_height / frame.shape[0]
                dimensions = (int(frame.shape[1] * ratio), frame_height)

                resized_frame = cv2.resize(annotated_frame, dimensions, interpolation=cv2.INTER_AREA)

                fps = cap.get(cv2.CAP_PROP_FPS)

                cv2.putText(
                    resized_frame,
                    'FPS: ' + str(fps),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA | cv2.FONT_HERSHEY_SIMPLEX)

                cv2.imshow('Challenge | Detector de Placas PARE e Semaforos', resized_frame)

        if cv2.waitKey(1) == 27:  # 27 é o código ASCII para 'Esc'
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()

# © 2023 CarAI.
