from mpi4py import MPI
import serial
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

ser = None  # Inicializa ser como None em todos os processos

if rank == 0:
    ser = serial.Serial('COM4', 9600, timeout=1)

def write_to_serial(data):
    if ser is not None:
        ser.write(data.encode())
        time.sleep(0.01)

        resposta_arduino = ser.readline().decode().strip()
        print(resposta_arduino)

try:
    while True:
        if rank == 0:
            angulo = 90
            esquerda_x = 64
            direita_x = 356
            offset = 11
            angulo_offset = 14

            dados_a_enviar = f'A{angulo},{esquerda_x},{direita_x},{offset},{angulo_offset}\n'

        elif rank == 1:
            placa_pare = 1
            semaforo = 3

            dados_a_enviar = f'B{placa_pare},{semaforo}\n'

        comm.Barrier()  # Sincroniza todos os processos antes de escrever

        write_to_serial(dados_a_enviar)

        comm.Barrier()  # Sincroniza todos os processos depois de escrever

        # Alternar entre os processos
        rank = 1 - rank

except KeyboardInterrupt:
    if rank == 0:
        ser.close()
