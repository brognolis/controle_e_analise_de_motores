# Título: Controle e Análise de Motor
# Alunos: Gabriel Brognoli, Israel Reus e Deivid Beppler
# Data de Criação: 23/11/2023
# Última Modificação: 06/12/2023
#
# AVISO: Para testar e utilizar o código corretamente é necessário utilizar um microcontrolador
#        compatível com Micro Python e com o firmware instalado e seguir o esquemático disponível no link abaixo:
#        link:

#==================================================================================================

from machine import Pin  # função de atribuir pinos do microcontrolador do módulo padrão do micro python
from time import sleep   # função de pausa do código do módulo time
import sys               # módulo de funções e comandos do sistema
import time              # módulo de tempo

#==================================================================================================
# --- Declaração de Variaveis ---

last_state = 0           # ultimo valor do botão
current_state = 0        # valor atual do botão
led_control = 0          # variavel de controle do led, 0 = desligado 1 = ligado
start = 0                # recebe o inicio do timer
end = 0                  # recebe o final do timer
loop_control = 0         # controla o loop do programa para não repetir certas funções
tempo_decorrido = 0      # armazena o tempo decorrido entre o começo e o fim do timer
block = 0

#==================================================================================================
# --- Coleta de Informações Iniciais ---

dado_tensao = float(input("Digite a tensão de trabalho do seu motor em volts(V): "))            # armazena a tensão de trabalho do motor
dado_corrente = float(input("Digite o consumo de corrente do seu motor em amperes(A): "))       # armazena a corrente de trabalho do motor
dado_energia = float(input("Digite o valor em reais pago por você por kWh: "))                  # armazena o valor do kWh do usuario

#==================================================================================================
# --- Definição dos Pinos ---

botao = Pin(5, Pin.IN, Pin.PULL_UP)   # define o pino do botao na porta 1 com resistor de pullup ativo
led = Pin(16, Pin.OUT)                # define o pino do led embutido
motor = Pin(4, Pin.OUT)               # define o pino de saída do motor

#==================================================================================================
# --- Definição de Funções ---

# Transforma o valor escrito no monitor serial em uma string
def ler_serial():
    
  bytes = []                       # Cria uma lista vazia para armazenar os bytes recebidos
  
  while True:                      # Cria um loop infinito
    
    byte = sys.stdin.read(1)       # Lê um byte do terminal serial
    
    if byte == "\n":               # Verifica se o byte é um caractere de nova linha (\n)
      string = "".join(bytes)      # Converte a lista de bytes em uma string
      return string                # Retorna a string
    
    else:
      bytes.append(byte)           # Adiciona o byte à lista

#==================================================================================================
# Faz o controle do que acontece ao ligar e desligar do led
def controle_e_analise():
    
    global last_state                              # ========================================
    global led_control                             #   
    global start                                   # 
    global end                                     #    declarando as variaveis globais
    global loop_control                            #          usadas nessa função
    global tempo_decorrido                         #          
    global custo_semanal                           #
    global custo_anual                             #
    global custo_mensal                            # ========================================
    
    current_state = not botao.value()              # estado atual recebe o valor digital do botão

    if current_state == 0:                         # se o estado atual do botao for igual a pressionado
        if last_state == 1:                        # e se o ultimo estado dele foi igual a solto
            led_control = 1 - led_control          # muda o estado da variavel de controle do led
                
    if led_control == 1:                           # se a variavel de controle do led for igual a 1
        led.off()                                  # liga o led (invertido)
        motor.on()
        if loop_control == 0:                      # se a variavel de controle do loop for igual a 0
            print("Status: Ligado")                # mostra o status do motor
            start = time.time_ns()                 # inicia a contagem do tempo (nanossegundos)
            loop_control = 1                       # coloca a variavel de loop em 1 para que esta seção só seja executada uma vez
        
    else:
        led.on()                                   # desliga o led (invertido)
        motor.off()
        if loop_control == 1:                      # se a variavel de controle de loop for igual a 1
            end = time.time_ns()                   # finaliza a contagem do tempo (nanossegundos)   
            print("Status: Desligado")             # mostra o status do motor
            tempo()                                # conta o tempo decorrido e separa em minutos e horas
            tempo_decorrido = (end - start) / 1e9  # variavel global do tempo
            analise_tempo()                        # faz as analises de custo e consumo de energia
            loop_control = 3                       # coloca a variavel de loop em 3 para que esta seção só seja executada uma vez
            
        if loop_control == 3:                      # entra no looping para perguntar a próxima ação que o usuario quer escolher
            pergunta_continuar()                   # chama função de modificação opicional dos dados do motor
        
    last_state = current_state                     # ao final, o ultimo estado recebe o estado atual
    return led.value()                             # retorna o nível lógico do led para fazer análise do funcionamento

#==================================================================================================
# Realiza os cálculos de custos e potencias da operação 
def analise_tempo():
    
    global dado_tensao                                          # ====================================================
    global dado_corrente                                        #   declarando as variaveis globais usadas na função
    global dado_energia                                         # ====================================================
    
    potencia = dado_tensao * dado_corrente                      # calculo da potencia do motor
    consumo_total = (potencia/1000) * (tempo_decorrido/3600)    # consumo total em kWh
    
    custo_dia = consumo_total * dado_energia                    # custo em kWh em uma operação no dia
    custo_semanal = custo_dia * 7                               # custo em kWh semanal dessa operação
    custo_mensal = custo_dia * 30                               # custo em kWh mensal dessa operação
    custo_anual = custo_dia * 365                               # custo em kWh anual dessa operação
    
    print("A potencia do motor é de: ", potencia, "W")                          # ====================================================
    print("O custo dessa operação foi de: R$", custo_dia)                       #
    print("O custo dessa operação semanalmente seria de: R$", custo_semanal)    #   print das mensagens dos custos de cada operação
    print("O custo dessa operação mensalmente seria de: R$", custo_mensal)      #
    print("O custo desaa operação anualmente seria de: R$", custo_anual)        # ====================================================
   
#==================================================================================================
# Calculo do tempo decorrido
def tempo():
    
    global start                       # declaração global da variavel de inicio do timer
    global end                         # declaração global da variavel de fim do timer
    
    tempo = (end - start) / 1e9        # o tempo decorrido recebe o valor final do timer menos o inicial em nanossegundos e transforma em segundos
    tempo_segundos = tempo             # tempo em segundos
    tempo_minutos = tempo // 60        # recebe apenas a parte inteira da divisão do tempo em segundos por 60
    tempo_horas = tempo_minutos // 60  # recebe apenas a parte inteira da divisão do tempo em minutos por 60
    
    
    if tempo_segundos > 59:                                                                          # se o tempo for maior que 59 segundos
        tempo_segundos = tempo_segundos % 60                                                         # tempo em segundos recebe o resto da divisão por 60(um minuto)
        print("O tempo decorrido foi de", tempo_minutos,"minuto(s) e", tempo_segundos,"segundos")    # printa o tempo decorrido
        
    elif tempo_minutos > 59:                                                                         # se o tempo for maior que 59 minutos
        tempo_minutos = tempo_horas % 60                                                             # tempo em minutos recebe o resto da divisão por 60(uma hora)
        tempo_segundos = tempo_segundos % 60                                                         # tempo em segundos recebe o resto da divisão por 60(um minuto)
        # printa o tempo decorrido
        print("O tempo decorrido foi de", tempo_horas, "hora(s),", tempo_minutos,"minutos e", tempo_segundos,"segundos")
        
    elif tempo_segundos < 60:                                                                        # se o tempo for menor que 60 segundos
        print("O tempo decorrido foi de", tempo_segundos,"segundos")                                 # printa o tempo decorrido

#==================================================================================================
# --- Pergunta pós finalização ---
def pergunta_continuar():
    
    global loop_control                                                                                 # =====================================================
    global dado_tensao                                                                                  #
    global dado_corrente                                                                                #   declarando as variaveis globais usadas na função
    global dado_energia                                                                                 #
    global block                                                                                        # =====================================================
    
    if block == 0:                                                                                      # se a variavel de block de loop do print for 0
        print("\nVocê deseja editar as configurações do motor? (\"sim\" ou \"nao\")")                     # printa a mensagem ao usuario
        block = 1                                                                                       # bloqueia o loop da mensagem
         
    resposta = ler_serial()                                                                             # variavel resposta recebe o valor escrito no monitor serial                                                                      
    
    if resposta == "nao":                                                                               # se o usuario escrever "nao" no monitor serial
        print("Ok, pode continuar com a operação normalmente!\n\n")                                     # printa a mensagem de continuidade 
        loop_control = 0                                                                                # desbloqueia as outras funções
        block = 0                                                                                       # reseta a variavel de block de loop do print
            
    if resposta == "sim":                                                                               # bloqueia as outras funções de acontecerem
        dado_tensao = float(input("Digite a tensão de trabalho do seu motor em volts(V): "))            # armazena a tensão de trabalho do motor
        dado_corrente = float(input("Digite o consumo de corrente do seu motor em amperes(A): "))       # armazena a corrente de trabalho do motor
        dado_energia = float(input("Digite o valor em reais pago por você por kWh: "))                  # armazena o valor do kWh do usuario
        print("Ok, pode continuar com a operação normalmente!\n\n")                                     # mensagem de sucesso na operação
        loop_control = 0                                                                                # desbloqueia as outras funções
        block = 0                                                                                       # reseta a variavel de block de loop do print
           
#==================================================================================================
# --- Looping de Código ---

while True:                     # looping infinito

    controle_e_analise()        # função principal em looping
    
    sleep(0.1)                  # da um tempo de 0,1 segundos
    