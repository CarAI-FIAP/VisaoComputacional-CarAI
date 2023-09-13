import tkinter
import tkinter.messagebox
import customtkinter
from customtkinter import CTkSwitch

customtkinter.set_appearance_mode('Dark')
customtkinter.set_default_color_theme('blue')

class PainelDeControle(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title('Painel de Controle - Visao Computacional')
        # self.geometry(f"{854}x{480}")

        # Configurações do layout grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Criar sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky='nsew')
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text='CarAI',
                                                 font=customtkinter.CTkFont(size=20, weight='bold'))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.botao_gerar_estatisticas = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.botao_gerar_estatisticas.grid(row=1, column=0, padx=20, pady=10)
        self.botao_gerar_estatisticas.configure(text='Gerar estatísticas')

        self.select_port_label = customtkinter.CTkLabel(master=self.sidebar_frame, text='Port:', anchor='w')
        self.select_port_label.grid(row=5, column=0, padx=20, pady=(20, 0))
        self.select_port = customtkinter.CTkComboBox(master=self.sidebar_frame,
                                                     values=['COM9', 'COM6', 'COM10', 'COM12', 'COM13'])
        self.select_port.grid(row=6, column=0, padx=20, pady=0)

        self.select_rate_label = customtkinter.CTkLabel(master=self.sidebar_frame, text='Rate:', anchor='w')
        self.select_rate_label.grid(row=7, column=0, padx=0, pady=(20, 0))
        self.select_rate = customtkinter.CTkComboBox(master=self.sidebar_frame,
                                                     values=['115200', '9600'])
        self.select_rate.grid(row=8, column=0, padx=0, pady=(0, 30))

        self.container_frame = customtkinter.CTkFrame(self)
        self.container_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.container_frame.grid_rowconfigure(1, weight=1)

        # Criar tabs
        self.tabview = customtkinter.CTkTabview(master=self.container_frame, width=550)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky='nsew')
        self.tabview.add('Configurações')
        self.tabview.add('Binarização')
        self.tabview.add('Imagem')
        self.tabview.add('Perspectiva')

        # Aba | Configurações gerais
        self.tabview.tab('Configurações').grid_columnconfigure(1, weight=1)

        self.switch_comunicacao_serial = customtkinter.CTkSwitch(master=self.tabview.tab('Configurações'),
                                                                 text='Habilitar comunicação serial c/ Arduino')
        self.switch_comunicacao_serial.grid(row=1, column=0, pady=(30, 10), padx=20, sticky='w')

        self.switch_birds_view = customtkinter.CTkSwitch(master=self.tabview.tab('Configurações'),
                                                         text='Habilitar perspectiva de pássaro')
        self.switch_birds_view.grid(row=2, column=0, pady=10, padx=20, sticky='w')

        self.switch_camera = customtkinter.CTkSwitch(master=self.tabview.tab('Configurações'),
                                                     text='Habilitar câmera')
        self.switch_camera.grid(row=3, column=0, pady=10, padx=20, sticky='w')

        self.switch_calibracao_camera = customtkinter.CTkSwitch(master=self.tabview.tab('Configurações'),
                                                                text='Habilitar calibração da câmera')
        self.switch_calibracao_camera.grid(row=4, column=0, pady=(10, 20), padx=20, sticky='w')

        self.select_coodernada_min_y_label = customtkinter.CTkLabel(master=self.tabview.tab('Configurações'),
                                                                 text='Coodernada min de identifcação no eixo y', anchor='w')
        self.select_coodernada_min_y_label.grid(row=5, column=0, padx=20, pady=0)
        self.select_coodernada_min_y = customtkinter.CTkComboBox(master=self.tabview.tab('Configurações'),
                                                              values=['200'])
        self.select_coodernada_min_y.grid(row=6, column=0, padx=20, pady=(0, 20))

        self.select_fator_reducao_label = customtkinter.CTkLabel(master=self.tabview.tab('Configurações'),
                                                                 text='Fator de redução', anchor='w')
        self.select_fator_reducao_label.grid(row=5, column=1, padx=20, pady=0)
        self.select_fator_reducao = customtkinter.CTkComboBox(master=self.tabview.tab('Configurações'),
                                                              values=['1', '2', '3', '4', '5', '6', '7', '8', '9',
                                                                      '10'])
        self.select_fator_reducao.grid(row=6, column=1, padx=20, pady=(0, 20))

        # Aba | Binarização personalizada por canais da imagem
        self.frame_canal_l = customtkinter.CTkFrame(master=self.tabview.tab('Binarização'))
        self.frame_canal_l.grid(row=1, column=0, padx=20, pady=(30, 20), sticky='nsew')

        self.switch_canal_l = customtkinter.CTkSwitch(master=self.frame_canal_l, text='Canal L',
                                                      font=customtkinter.CTkFont(size=12, weight='normal'))
        self.switch_canal_l.grid(row=1, column=0, pady=20, padx=20, sticky='w')

        self.canal_l_max = tkinter.DoubleVar()
        self.canal_l_min = tkinter.DoubleVar()

        self.slider_canal_l_min = customtkinter.CTkSlider(master=self.frame_canal_l, from_=0, to=1,
                                                          variable=self.canal_l_min, width=120,
                                                          number_of_steps=20)
        self.slider_canal_l_min.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_l_min = customtkinter.CTkEntry(master=self.frame_canal_l, width=50,
                                                        textvariable=self.canal_l_min)
        self.input_canal_l_min.grid(row=2, column=1, padx=(0, 20), pady=0, sticky='w')
        self.slider_canal_l_max = customtkinter.CTkSlider(master=self.frame_canal_l, from_=0, to=1,
                                                          variable=self.canal_l_max, width=120,
                                                          number_of_steps=20)
        self.slider_canal_l_max.grid(row=4, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_l_max = customtkinter.CTkEntry(master=self.frame_canal_l, width=50,
                                                        textvariable=self.canal_l_max)
        self.input_canal_l_max.grid(row=4, column=1, padx=(0, 20), pady=20, sticky='w')

        self.frame_canal_h = customtkinter.CTkFrame(master=self.tabview.tab('Binarização'))
        self.frame_canal_h.grid(row=1, column=1, padx=20, pady=(30, 20), sticky='nsew')

        self.switch_canal_h = customtkinter.CTkSwitch(master=self.frame_canal_h, text='Canal H',
                                                      font=customtkinter.CTkFont(size=12, weight='normal'))
        self.switch_canal_h.grid(row=1, column=0, pady=20, padx=20, sticky='w')

        self.canal_h_max = tkinter.DoubleVar()
        self.canal_h_min = tkinter.DoubleVar()

        self.slider_canal_h_min = customtkinter.CTkSlider(master=self.frame_canal_h, from_=0, to=255,
                                                          variable=self.canal_h_min, width=120,
                                                          number_of_steps=51)
        self.slider_canal_h_min.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_h_min = customtkinter.CTkEntry(master=self.frame_canal_h, width=50,
                                                        textvariable=self.canal_h_min)
        self.input_canal_h_min.grid(row=2, column=1, padx=(0, 20), pady=0, sticky='w')
        self.slider_canal_h_max = customtkinter.CTkSlider(master=self.frame_canal_h, from_=0, to=255,
                                                          variable=self.canal_h_max, width=120,
                                                          number_of_steps=51)
        self.slider_canal_h_max.grid(row=4, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_h_max = customtkinter.CTkEntry(master=self.frame_canal_h, width=50,
                                                        textvariable=self.canal_h_max)
        self.input_canal_h_max.grid(row=4, column=1, padx=(0, 20), pady=20, sticky='w')

        self.frame_canal_v = customtkinter.CTkFrame(master=self.tabview.tab('Binarização'))
        self.frame_canal_v.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')

        self.switch_canal_v = customtkinter.CTkSwitch(master=self.frame_canal_v, text='Canal V',
                                                      font=customtkinter.CTkFont(size=12, weight='normal'))
        self.switch_canal_v.grid(row=1, column=0, pady=20, padx=20, sticky='w')

        self.canal_v_max = tkinter.DoubleVar()
        self.canal_v_min = tkinter.DoubleVar()

        self.slider_canal_v_min = customtkinter.CTkSlider(master=self.frame_canal_v, from_=0, to=1,
                                                          variable=self.canal_v_min, width=120,
                                                          number_of_steps=20)
        self.slider_canal_v_min.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_v_min = customtkinter.CTkEntry(master=self.frame_canal_v, width=50,
                                                        textvariable=self.canal_v_min)
        self.input_canal_v_min.grid(row=2, column=1, padx=(0, 20), pady=0, sticky='w')
        self.slider_canal_v_max = customtkinter.CTkSlider(master=self.frame_canal_v, from_=0, to=1,
                                                          variable=self.canal_v_max, width=120,
                                                          number_of_steps=20)
        self.slider_canal_v_max.grid(row=4, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_v_max = customtkinter.CTkEntry(master=self.frame_canal_v, width=50,
                                                        textvariable=self.canal_v_max)
        self.input_canal_v_max.grid(row=4, column=1, padx=(0, 20), pady=20, sticky='w')

        self.frame_canal_s = customtkinter.CTkFrame(master=self.tabview.tab('Binarização'))
        self.frame_canal_s.grid(row=2, column=1, padx=20, pady=20, sticky='nsew')

        self.switch_canal_s = customtkinter.CTkSwitch(master=self.frame_canal_s, text='Canal S',
                                                      font=customtkinter.CTkFont(size=12, weight='normal'))
        self.switch_canal_s.grid(row=1, column=0, pady=20, padx=20, sticky='w')

        self.canal_s_max = tkinter.DoubleVar()
        self.canal_s_min = tkinter.DoubleVar()

        self.slider_canal_s_min = customtkinter.CTkSlider(master=self.frame_canal_s, from_=0, to=255,
                                                          variable=self.canal_s_min, width=120,
                                                          number_of_steps=51)
        self.slider_canal_s_min.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_s_min = customtkinter.CTkEntry(master=self.frame_canal_s, width=50,
                                                        textvariable=self.canal_s_min)
        self.input_canal_s_min.grid(row=2, column=1, padx=(0, 20), pady=0, sticky='w')
        self.slider_canal_s_max = customtkinter.CTkSlider(master=self.frame_canal_s, from_=0, to=255,
                                                          variable=self.canal_s_max, width=120,
                                                          number_of_steps=51)
        self.slider_canal_s_max.grid(row=4, column=0, padx=20, pady=0, sticky='w')
        self.input_canal_s_max = customtkinter.CTkEntry(master=self.frame_canal_s, width=50,
                                                        textvariable=self.canal_s_max)
        self.input_canal_s_max.grid(row=4, column=1, padx=(0, 20), pady=20, sticky='w')

        # Aba | Tratamento de imagem
        self.switch_threshold_tradicional = customtkinter.CTkSwitch(master=self.tabview.tab('Imagem'),
                                                                 text='Habilitar threshold tradicional')
        self.switch_threshold_tradicional.grid(row=0, column=0, pady=(30, 20), padx=20, sticky='w')

        self.frame_thresh = customtkinter.CTkFrame(master=self.tabview.tab('Imagem'))
        self.frame_thresh.grid(row=1, column=0, padx=20, pady=(0, 20), sticky='nsew')

        self.thresh_max = tkinter.DoubleVar()
        self.thresh_min = tkinter.DoubleVar()

        self.slider_thresh_min = customtkinter.CTkSlider(master=self.frame_thresh, from_=0, to=255,
                                                          variable=self.thresh_min, width=120,
                                                          number_of_steps=51)
        self.slider_thresh_min.grid(row=1, column=0, padx=20, pady=(20, 0), sticky='w')
        self.input_thresh_min = customtkinter.CTkEntry(master=self.frame_thresh, width=50,
                                                        textvariable=self.thresh_min)
        self.input_thresh_min.grid(row=1, column=1, padx=(0, 20), pady=(20, 0), sticky='w')
        self.slider_thresh_max = customtkinter.CTkSlider(master=self.frame_thresh, from_=0, to=255,
                                                          variable=self.thresh_max, width=120,
                                                          number_of_steps=51)
        self.slider_thresh_max.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.input_thresh_max = customtkinter.CTkEntry(master=self.frame_thresh, width=50,
                                                        textvariable=self.thresh_max)
        self.input_thresh_max.grid(row=2, column=1, padx=(0, 20), pady=20, sticky='w')

        self.select_thresh_tipo = customtkinter.CTkComboBox(master=self.frame_thresh,
                                                              values=['cv2.THRESH_BINARY + cv2.THRESH_OTSU'])
        self.select_thresh_tipo.grid(row=2, column=2, padx=(0, 20), pady=20)

        # Aba | Transformação de perspectiva
        self.frame_xfd = customtkinter.CTkFrame(master=self.tabview.tab('Perspectiva'))
        self.frame_xfd.grid(row=1, column=0, padx=20, pady=(30, 0), sticky='nsew')

        self.xfd_valor = tkinter.DoubleVar()

        self.slider_xfd = customtkinter.CTkSlider(master=self.frame_xfd, from_=0, to=1280,
                                                          variable=self.xfd_valor, width=200,
                                                          number_of_steps=1280)
        self.slider_xfd.grid(row=0, column=0, padx=20, pady=20, sticky='w')
        self.input_xfd = customtkinter.CTkEntry(master=self.frame_xfd, width=50,
                                                        textvariable=self.xfd_valor)
        self.input_xfd.grid(row=0, column=1, padx=(0, 20), pady=20, sticky='w')

        self.xfd_label = customtkinter.CTkLabel(master=self.frame_xfd, text='xfd', anchor='w',
                                                font=customtkinter.CTkFont(size=14, weight='normal'))
        self.xfd_label.grid(row=0, column=2, padx=20, pady=20)

        self.frame_yf = customtkinter.CTkFrame(master=self.tabview.tab('Perspectiva'))
        self.frame_yf.grid(row=2, column=0, padx=20, pady=25, sticky='nsew')

        self.yf_valor = tkinter.DoubleVar()

        self.slider_yf = customtkinter.CTkSlider(master=self.frame_yf, from_=0, to=720,
                                                          variable=self.yf_valor, width=200,
                                                          number_of_steps=720)
        self.slider_yf.grid(row=0, column=0, padx=20, pady=20, sticky='w')
        self.input_yf = customtkinter.CTkEntry(master=self.frame_yf, width=50,
                                                        textvariable=self.yf_valor)
        self.input_yf.grid(row=0, column=1, padx=(0, 20), pady=20, sticky='w')

        self.yf_label = customtkinter.CTkLabel(master=self.frame_yf, text='yf', anchor='w',
                                                font=customtkinter.CTkFont(size=14, weight='normal'))
        self.yf_label.grid(row=0, column=2, padx=20, pady=20)

        self.frame_offset_x = customtkinter.CTkFrame(master=self.tabview.tab('Perspectiva'))
        self.frame_offset_x.grid(row=3, column=0, padx=20, pady=(0, 10), sticky='nsew')

        self.offset_x_valor = tkinter.DoubleVar()

        self.slider_offset_x = customtkinter.CTkSlider(master=self.frame_offset_x, from_=0, to=1280,
                                                          variable=self.offset_x_valor, width=200,
                                                          number_of_steps=1280)
        self.slider_offset_x.grid(row=0, column=0, padx=20, pady=20, sticky='w')
        self.input_offset_x = customtkinter.CTkEntry(master=self.frame_offset_x, width=50,
                                                        textvariable=self.offset_x_valor)
        self.input_offset_x.grid(row=0, column=1, padx=(0, 20), pady=20, sticky='w')

        self.offset_x_label = customtkinter.CTkLabel(master=self.frame_offset_x, text='offset x', anchor='w',
                                                font=customtkinter.CTkFont(size=14, weight='normal'))
        self.offset_x_label.grid(row=0, column=2, padx=20, pady=20)


        self.checkbox_altura_camera = customtkinter.CTkCheckBox(master=self.tabview.tab('Perspectiva'),
                                                                text='A câmera está posicionada em uma altura baixa')
        self.checkbox_altura_camera.grid(row=4, column=0, pady=20, padx=20, sticky='w')

        # Valores padrão
        self.select_fator_reducao.set('3')

        self.switch_canal_l.select()
        self.canal_l_min.set(0.75)
        self.canal_l_max.set(1)
        self.switch_canal_h.select()
        self.canal_h_min.set(20)
        self.canal_h_max.set(30)
        self.switch_canal_v.select()
        self.canal_v_min.set(0.85)
        self.canal_v_max.set(1)
        self.canal_s_min.set(30)
        self.canal_s_max.set(255)

        self.thresh_min.set(115)
        self.thresh_max.set(255)

        self.xfd_valor.set(162)
        self.yf_valor.set(450)
        self.offset_x_valor.set(0)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text='Type in a number:', title='CTkInputDialog')
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace('%', '')) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print('sidebar_button click')


if __name__ == '__main__':
    painel = PainelDeControle()
    painel.mainloop()
    painel.update_idletasks()  # Atualiza o layout
    painel.geometry(
        f'{painel.winfo_reqwidth()}x{painel.winfo_reqheight()}')  # Define o tamanho da janela com base no layout
