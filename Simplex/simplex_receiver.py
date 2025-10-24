# simplex_receiver.py
import machine
import utime
from micropython import const

# Configurar UART para RS485
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# LED indicador
led = machine.Pin(25, machine.Pin.OUT)

# Variables de estadísticas
packet_count = 0
error_count = 0
last_packet_time = utime.ticks_ms()

def calculate_checksum(data):
    return sum(data) & 0xFF

def process_packet(packet):
    global packet_count, error_count
    
    if len(packet) < 5:  # Mínimo: tipo(1) + data(2) + seq(1) + checksum(1)
        error_count += 1
        return None
    
    # Verificar checksum
    received_checksum = packet[-1]
    calculated_checksum = calculate_checksum(packet[:-1])
    
    if received_checksum != calculated_checksum:
        error_count += 1
        return None
    
    packet_count += 1
    
    # Extraer datos del paquete
    packet_type = packet[0]
    data_value = (packet[1] << 8) | packet[2]
    sequence = packet[3]
    
    return {
        'type': packet_type,
        'data': data_value,
        'sequence': sequence,
        'timestamp': utime.ticks_ms()
    }

print("Esclavo Simplex - Listo para recibir...")

while True:
    if uart.any():
        # Leer datos disponibles
        data = uart.read()
        
        if data:
            # Procesar cada byte
            for byte in data:
                packet = process_packet(byte)  # Aquí deberías implementar un protocolo real
                if packet:
                    led.toggle()
                    print(f"Paquete {packet['sequence']}: Dato={packet['data']}")
    
    # Enviar estadísticas cada 10 segundos (por UART adicional si es necesario)
    if utime.ticks_diff(utime.ticks_ms(), last_packet_time) > 10000:
        print(f"Estadísticas: Paquetes={packet_count}, Errores={error_count}")
        last_packet_time = utime.ticks_ms()
    
    utime.sleep_ms(10)