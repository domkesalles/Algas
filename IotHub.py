import struct
import sys
import math
import time
import random
import mysql.connector 
import numpy as np
from azure.iot.device import IoTHubDeviceClient, Message

#Connection String
def conect_iothub():
    CONNECTION_STRING = "HostName=felipe02211014.azure-devices.net;DeviceId=felipe02211014;SharedAccessKey=VF07EY0+x/zxedBziCYQW/qVVt+8DuYUCtCFHp5FDfA="
    return IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def send_message(message):
    DEVICE_ID = "felipe02211014"
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    message.custom_properties["device_id"] = DEVICE_ID
    sensor = conect_iothub()
    sensor.connect()
    print("Enviando mensagem:", message)
    sensor.send_message(message)
    sensor.shutdown()

# Criação de listas
lista_decibel = []
lista_ambiente = []
lista_espaco = []
lista_tempo = []

bateria = 100.0

# Configurações da gravação de áudio simulado
CHUNK = 1024
RATE = 44100

# Define o limiar de ruído máximo permitido (em dB)
MAX_NOISE_LEVEL = 45

# def conect_banco():
#     try:
#         conn = mysql.connector.connect(host="localhost", user="root", password="Renato2002", database="ruido", port="3306")
#         print("Conexão com banco de dados feita\n")
#         return conn
#     except mysql.connector.Error as error:
#         if error.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database doesn't exist")
#         elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("User name or password is wrong")
#         else:
#             print(error)

def insert_mysql_connector(decibel, ambiente, espaco, duracao):
    try:
        mydb = mysql.connector.connect(
            host = "nivel-ruido.mysql.database.azure.com",
            user = "roott",
            password = "Urubu100",
            database = "ruido",
            ssl_ca = "DigiCertGlobalRootCA.crt.pem",
            port = "3306")

        if mydb.is_connected():
            db_Info = mydb.get_server_info()
            print("Conectado ao MySQL Server", db_Info)

            mycursor = mydb.cursor()

            sql_query = "INSERT INTO nivel_ruido (decibel, ambiente, espaco, duracao) VALUES (%s, %s, %s, %s);"
            val = [decibel, ambiente, espaco, duracao]
            mycursor.execute(sql_query, val)
            mydb.commit()

            print(mycursor.rowcount, "Registro Inserido com Sucesso!")
    except mysql.connector.Error as e:
        print("Erro ao conectar com o MySQL:", e)
    finally:
        if(mydb.is_connected()):
            mycursor.close()
            mydb.close()
            print("Conexão com MySQL está Fechada!\n")

def calculate_noise_level(data):
    # Converte os dados do áudio em um array de números inteiros
    data_int = struct.unpack(str(len(data)) + 'B', data)

    # Calcula a energia do sinal
    rms = math.sqrt(sum([(x - 128) ** 2 for x in data_int]) / len(data_int))

    # Calcula o nível de ruído em dB usando a escala A de ponderação de frequência
    decibel = 20 * math.log10(rms)

    return decibel

def medir_nivel_ruido(tempo_medicao, bateria):

    inicio_processamento = time.time()

    # Inicializa a variável como verdadeira
    ambiente_adequado = True
    ambiente_simulado = True

    #Variável que vai pro banco
    ambiente = ""
    ambiente_2 = ""

    # Calcula o número de chunks para gerar com base no tempo de medição
    num_chunks = int(RATE / CHUNK * tempo_medicao)

    # Inicializa a lista para armazenar os dados de áudio simulados
    data_list = []

    # Gera os dados de áudio simulados
    for i in range(num_chunks):
        data = np.random.randint(-32768, 32767, CHUNK, dtype=np.int16).tobytes()
        data_list.append(data)

    # Concatena os dados de áudio simulados em uma única string
    data_concatenado = b''.join(data_list)

    # Calcula o nível de ruído em dB
    decibel = calculate_noise_level(data_concatenado)
    decibel_simulado = round(random.normalvariate(decibel, 40), 2)
    while (decibel_simulado <= 0):
        decibel_simulado = round(random.normalvariate(decibel, 40), 2)

    # Imprime as informações do nível de ruído
    print(f"Nível de ruído durante {tempo_medicao} segundos: {decibel:.2f} dB")

    # Verifica se o nível de ruído está acima do limiar máximo permitido
    if decibel > MAX_NOISE_LEVEL:
        print("O ambiente não está adequado para o sono do paciente")
        ambiente_adequado = False
        ambiente = "Não Adequado"
    else:
        print("O ambiente está adequado para o sono do paciente")
        ambiente_adequado = True
        ambiente = "Adequado"

    # Imprime as informações do nível de ruído
    print(f"Nível de ruído simulado durante {tempo_medicao} segundos: {decibel_simulado:.2f} dB")

    # Verifica se o nível de ruído está acima do limiar máximo permitido
    if decibel_simulado > MAX_NOISE_LEVEL:
        print("O ambiente simulado não está adequado para o sono do paciente")
        ambiente_simulado = False
        ambiente_2 = "Não Adequado"
    else:
        print("O ambiente simulado está adequado para o sono do paciente")
        ambiente_simulado = True
        ambiente_2 = "Adequado"

    # Simulação da gravação do áudio
    time.sleep(0.01)  # Simula o tempo de gravação do áudio

    lista_decibel.append(decibel_simulado)
    lista_ambiente.append(ambiente_simulado)

    fim_processamento = time.time()
    duracao = fim_processamento - inicio_processamento
    espaco = sys.getsizeof(lista_decibel) / (1024 * 1024)

    lista_espaco.append(espaco)
    lista_tempo.append(duracao)

    insert_mysql_connector(decibel=decibel, ambiente=ambiente, espaco=espaco, duracao=duracao)
    insert_mysql_connector(decibel=decibel_simulado, ambiente=ambiente_2, espaco=espaco, duracao=duracao)

    message = Message('{"decibel": %f, "ambiente": %s, "espaco": %f, "duracao": %s, "bateria": %.2f}' % (decibel_simulado, str(ambiente_2), espaco, duracao, bateria))
    send_message(message)      

    return ambiente_adequado, ambiente_simulado

num_amostras = 1000000
tempo_medicao = 1
lista_ambiente_adequado = []
lista_ambiente_simulado = []

for i in range(num_amostras):
    ambiente_adequado, ambiente_simulado = medir_nivel_ruido(tempo_medicao, bateria)
    bateria -= 0.01 / 100 * bateria
    lista_ambiente_adequado.append(ambiente_adequado)
    lista_ambiente_simulado.append(ambiente_simulado)
