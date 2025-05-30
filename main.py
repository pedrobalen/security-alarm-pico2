import network
import time
from machine import Pin

SSID = 'S20'
PASSWORD = 'civic1999'

led = Pin("LED", Pin.OUT)

def piscar_led(intervalo=0.3):
    led.on()
    time.sleep(intervalo)
    led.off()
    time.sleep(intervalo)

def conectar_wifi(ssid, password, max_tentativas=30):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("🔄 Tentando conectar ao Wi-Fi...")
    tentativas = 0

    while not wlan.isconnected() and tentativas < max_tentativas:
        piscar_led()
        tentativas += 1

    if wlan.isconnected():
        print("✅ Conectado ao Wi-Fi!")
        print("📡 IP:", wlan.ifconfig()[0])
        return True
    else:
        print("❌ Falha ao conectar após", max_tentativas, "tentativas.")
        return False

def led_conectado():
    """Acende o LED fixo indicando conexão"""
    led.value(1)

def main():
    conectado = conectar_wifi(SSID, PASSWORD)

    if conectado:
        led_conectado()
    else:
        led.value(0)
        
if __name__ == "__main__":
    main()
