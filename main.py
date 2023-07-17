import cv2
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
        out_img = np.copy(img)

        #img = self.calibracao.corrigir_distorcao(img)
        img_warped = self.transformacao.mudar_perspectiva(img)
        img_threshold = self.tratamento.binarizar_imagem(img)
        img_filtrada = self.tratamento.aplicar_filtros(img_threshold)
        img_roi = self.tratamento.desenhar_roi(img_filtrada)

        cv2.imshow('img_roi', img_roi)

        histograma = self.faixas.calcular_histograma_pista(img_roi)
        pico_esquerda, pico_direita = self.faixas.calcular_picos_do_histograma(histograma)
        print('peak_left', pico_esquerda)
        print('pico_direita', pico_direita)
        cv2.line(out_img, (pico_esquerda, 0), (pico_esquerda, img.shape[0]), (0, 0, 255), 10)
        cv2.line(out_img, (pico_direita, 0), (pico_direita, img.shape[0]), (0, 0, 255), 10)

        return out_img

    def processar_video(self, input_path):
        cap = cv2.VideoCapture(input_path)

        while cap.isOpened():
            _, frame = cap.read()

            out_frame = self.identificar_faixas(frame)

            cv2.imshow('Video', out_frame)

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def main():
    identificaFaixas = IdentificaFaixasDeTransito()
    identificaFaixas.processar_video('assets/videos_teste/challenge_teatro.mp4')

if __name__ == "__main__":
    main()