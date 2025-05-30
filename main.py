import network
import urequests
import time
from machine import Pin

SSID = ""
PASSWORD = ""

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Conectando ao Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Conectado:", wlan.ifconfig())

def enviar_alerta_whatsapp(mensagem):
    telefone = "+" 
    apikey = ""
    mensagem_formatada = mensagem.replace(" ", "+")
    url = f"https://api.callmebot.com/whatsapp.php?phone={telefone}&text={mensagem_formatada}&apikey={apikey}"
    
    try:
        resposta = urequests.get(url)
        print("Mensagem enviada:", resposta.text)
        resposta.close()
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def sensor_detectou_presenca():
    return True  # teste sem sensor

def main():
    conectar_wifi()
    
    while True:
        if sensor_detectou_presenca():
            enviar_alerta_whatsapp("Movimento detectada")
            time.sleep(10)  

main()

