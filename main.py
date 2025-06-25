import network
import urequests
import time
import ubinascii
from machine import Pin
import gc

WIFI_SSID = 
WIFI_PASSWORD = 

TWILIO_ACCOUNT_SID = 
TWILIO_AUTH_TOKEN = 
TWILIO_PHONE_NUMBER = 
DESTINATION_PHONE = 
trig_pin = Pin(15, Pin.OUT)
echo_pin = Pin(14, Pin.IN)

led = Pin("LED", Pin.OUT)

SOUND_SPEED = 340
TRIG_PULSE_DURATION_US = 10

DISTANCIA_LIMITE = 20
INTERVALO_MEDICAO = 0.25
COOLDOWN_SMS = 20

ultimo_sms = 0

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"🌐 Conectando ao WiFi {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            print(f"✅ WiFi conectado! IP: {wlan.ifconfig()[0]}")
            return True
        else:
            print("❌ Falha na conexão WiFi!")
            return False
    return True

def medir_distancia():
    try:
        trig_pin.off()
        time.sleep_us(2)
        trig_pin.on()
        time.sleep_us(TRIG_PULSE_DURATION_US)
        trig_pin.off()
        
        timeout_start = time.ticks_us()
        while echo_pin.value() == 0:
            if time.ticks_diff(time.ticks_us(), timeout_start) > 30000:
                return None
        
        inicio_echo = time.ticks_us()
        
        while echo_pin.value() == 1:
            if time.ticks_diff(time.ticks_us(), inicio_echo) > 30000:
                return None
        
        fim_echo = time.ticks_us()
        ultrason_duration = time.ticks_diff(fim_echo, inicio_echo)
        distance_cm = ultrason_duration * SOUND_SPEED / 2 * 0.0001
        
        return distance_cm if 2 <= distance_cm <= 400 else None
        
    except:
        return None

def formatar_horario():
    agora = time.localtime()
    return f"{agora[2]:02d}/{agora[1]:02d}/{agora[0]} às {agora[3]:02d}:{agora[4]:02d}:{agora[5]:02d}"

def enviar_sms(mensagem):
    global ultimo_sms
    
    if time.time() - ultimo_sms < COOLDOWN_SMS:
        print("⏳ SMS em cooldown, aguardando...")
        return False
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
        auth_string = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = ubinascii.b2a_base64(auth_bytes).decode('ascii').strip()
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = f"From={TWILIO_PHONE_NUMBER}&To={DESTINATION_PHONE}&Body={mensagem}"
        
        print("📱 Enviando SMS...")
        response = urequests.post(url, data=data, headers=headers)
        
        if response.status_code == 201:
            print("✅ SMS enviado com sucesso!")
            ultimo_sms = time.time()
            
            for _ in range(3):
                led.on()
                time.sleep(0.2)
                led.off()
                time.sleep(0.2)
            
            response.close()
            return True
        else:
            print(f"❌ Erro ao enviar SMS: Status {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar SMS: {e}")
        return False
    finally:
        gc.collect()

def main():
    led.on()
    time.sleep(1)
    led.off()
    
    if not conectar_wifi():
        print("❌ WiFi necessário para funcionar!")
        return
    
    for _ in range(5):
        medir_distancia()
        time.sleep(0.1)
    
    print(f"Sistema ativo! Distância limite: {DISTANCIA_LIMITE}cm")
    print("-" * 40)
    
    movimento_detectado = False
    
    while True:
        try:
            distancia = medir_distancia()
            
            if distancia is not None:
                if distancia < DISTANCIA_LIMITE:
                    if not movimento_detectado:
                        horario = formatar_horario()
                        print(f"🚨 MOVIMENTO DETECTADO!")
                        print(f"   📏 Distância: {distancia:.1f}cm")
                        print(f"   🕒 Horário: {horario}")
                        
                        movimento_detectado = True
                        
                        mensagem = f"ALERTA: Movimento detectado! Objeto a {distancia:.1f}cm do sensor. Horário: {horario}"
                        enviar_sms(mensagem)
                        
                        for _ in range(5):
                            led.on()
                            time.sleep(0.1)
                            led.off()
                            time.sleep(0.1)
                        
                        print("Aguardando área ficar livre...")
                
                else:
                    if movimento_detectado:
                        print("Área livre - Sistema rearmado")
                        movimento_detectado = False
            
            time.sleep(INTERVALO_MEDICAO)
            
        except KeyboardInterrupt:
            print("\n🛑 Sistema interrompido pelo usuário")
            led.off()
            break
        except Exception as e:
            print(f"❌ Erro no sistema: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
