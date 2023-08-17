import serial
import time

# Definindo parâmetros de conexão
port = 'COM6'   # conferir porta que o arduino está conectado
rate = 115200
conn = serial.Serial(port, rate)
time.sleep(2)

while True:
    # Input do usuário
    grau = input(str("Informe o grau desejado (X para sair): ")).upper()
    print(grau)

    data = {
        'angulo_D': 2,
        'angulo_E': 2,
        'offset': 10,
    }

    if grau == "X":
        break

    else:
        grau = grau.encode('utf-8')

        # Comunicação serial
        conn.write(grau)
        time.sleep(1)

    # Resetando a variável dado
    conn.write(grau)

conn.close()