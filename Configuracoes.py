from PainelDeControle import *

class Configuracoes:
    def __init__(self):
        self.painel_de_controle = PainelDeControle()

        self.perspectiva_habilitada = self.get_birds_view()
        self.camera_faixas_habilitada = bool(self.painel_de_controle.switch_camera_faixas.get())
        self.camera_sinalizacao_habilitada = bool(self.painel_de_controle.switch_camera_sinalizacao.get())
        self.fator_reducao = int(self.painel_de_controle.select_fator_reducao.get())

        # Aba | Binarização personalizada por canais da imagem

        self.canal_l_habilitado = bool(self.painel_de_controle.switch_canal_l.get())
        self.canal_l_min = float(self.painel_de_controle.canal_l_min.get())
        self.canal_l_max = float(self.painel_de_controle.canal_l_max.get())
        self.canal_h_habilitado = bool(self.painel_de_controle.switch_canal_h.get())
        self.canal_h_min = int(self.painel_de_controle.canal_h_min.get())
        self.canal_h_max = int(self.painel_de_controle.canal_h_max.get())
        self.canal_v_habilitado = bool(self.painel_de_controle.switch_canal_v.get())
        self.canal_v_min = float(self.painel_de_controle.canal_v_min.get())
        self.canal_v_max = float(self.painel_de_controle.canal_v_max.get())
        self.canal_s_habilitado = bool(self.painel_de_controle.switch_canal_s.get())
        self.canal_s_min = float(self.painel_de_controle.canal_s_min.get())
        self.canal_s_max = float(self.painel_de_controle.canal_s_max.get())

        # Aba | Tratamento de imagem

        self.threshold_tradicional_habilitado = bool(self.painel_de_controle.switch_threshold_tradicional.get())
        self.thresh_min = int(self.painel_de_controle.thresh_min.get())
        self.thresh_max = int(self.painel_de_controle.thresh_max.get())
        self.thresh_tipo = self.painel_de_controle.select_thresh_tipo.get()

        # Aba | Transformação de perspectiva

        self.perspectiva_retangular_habilitada = bool(self.painel_de_controle.switch_perspectiva_retangular.get())
        self.xfd_valor = int(self.painel_de_controle.xfd_valor.get())
        self.yf_valor = int(self.painel_de_controle.yf_valor.get())
        self.offset_x = int(self.painel_de_controle.offset_x_valor.get())

    # Aba | Configurações gerais
    def get_arduino_port(self):
        return self.painel_de_controle.select_port.get()

    def get_arduino_rate(self):
        return int(self.painel_de_controle.select_rate.get())

    def get_switch_comunicacao_serial(self):
        return bool(self.painel_de_controle.switch_comunicacao_serial.get())

    def get_birds_view(self):
        birds_view = bool(self.painel_de_controle.switch_birds_view.get())

        return birds_view

    def inicializar_painel_de_controle(self):
        self.painel_de_controle.mainloop()
