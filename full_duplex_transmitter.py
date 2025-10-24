# full_duplex_transmitter.py
import machine
import utime
import json

# Configurar UART para transmisión
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# Sensor simulado (potenciómetro o temperatura)
sensor = machine.ADC(26)  # GP26 para entrada analógica

# Variables
sequence_number = 0
transmission_count = 0

def create_packet(sensor_value, packet_type=0x01):
    global sequence_number
    
    packet = bytearray()
    packet.append(packet_type)  # Tipo de paquete
    packet.append((sensor_value >> 8) & 0xFF)  # Byte alto
    packet.append(sensor_value & 0xFF)  # Byte bajo
    packet.append(sequence_number & 0xFF)  # Número de secuencia
    
    # Calcular checksum
    checksum = sum(packet) & 0xFF
    packet.append(checksum)
    
    sequence_number += 1
    return packet

print("Transmisor Full Duplex - Iniciado...")

while True:
    # Leer sensor
    sensor_value = sensor.read_u16()
    
    # Crear paquete
    packet = create_packet(sensor_value)
    
    # Transmitir
    uart.write(packet)
    transmission_count += 1
    
    # LED indicador
    machine.Pin(25, machine.Pin.OUT).toggle()
    
    print(f"Transmitido: {sensor_value}, Secuencia: {sequence_number-1}")
    
    utime.sleep_ms(1000)  # Transmitir cada segundo