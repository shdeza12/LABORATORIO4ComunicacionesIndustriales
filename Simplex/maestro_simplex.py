# maestro_simplex.py
import serial
import time
import struct
import threading
from datetime import datetime

class RS485SimplexMaster:
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.sequence_number = 0
        self.stats = {
            'tx_packets': 0,
            'tx_bytes': 0,
            'start_time': time.time()
        }
        
    def calculate_checksum(self, data):
        return sum(data) & 0xFF
    
    def create_packet(self, data_value, packet_type=0x01):
        packet = bytearray()
        packet.append(packet_type)
        packet.extend(struct.pack('>H', data_value))  # 2 bytes big-endian
        packet.append(self.sequence_number & 0xFF)
        
        checksum = self.calculate_checksum(packet)
        packet.append(checksum)
        
        self.sequence_number += 1
        return packet
    
    def transmit_data(self, data_value):
        packet = self.create_packet(data_value)
        self.ser.write(packet)
        
        self.stats['tx_packets'] += 1
        self.stats['tx_bytes'] += len(packet)
        
        return packet
    
    def get_statistics(self):
        uptime = time.time() - self.stats['start_time']
        return {
            'tx_packets': self.stats['tx_packets'],
            'tx_bytes': self.stats['tx_bytes'],
            'uptime': uptime,
            'data_rate': self.stats['tx_bytes'] / uptime if uptime > 0 else 0
        }

# Uso del maestro simplex
if __name__ == "__main__":
    master = RS485SimplexMaster()
    
    try:
        counter = 0
        while True:
            # Transmitir dato simulado
            data = counter % 1000
            packet = master.transmit_data(data)
            
            print(f"Transmitido: {data}, Paquete: {packet.hex()}")
            
            # Estadísticas cada 10 transmisiones
            if counter % 10 == 0:
                stats = master.get_statistics()
                print(f"Estadísticas: {stats}")
            
            counter += 1
            time.sleep(2)
            
    except KeyboardInterrupt:
        master.ser.close()