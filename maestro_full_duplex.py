# maestro_full_duplex.py
import serial
import time
import struct
import threading
import RPi.GPIO as GPIO

class RS485FullDuplexMaster:
    def __init__(self, tx_port='/dev/ttyAMA0', rx_port='/dev/ttyUSB0', baudrate=9600):
        # Configurar GPIO para control DE/RE
        GPIO.setmode(GPIO.BCM)
        self.tx_control_pin = 18
        self.rx_control_pin = 23
        
        GPIO.setup(self.tx_control_pin, GPIO.OUT)
        GPIO.setup(self.rx_control_pin, GPIO.OUT)
        
        # Puerto TX (transmisión)
        self.tx_ser = serial.Serial(tx_port, baudrate, timeout=0.1)
        # Puerto RX (recepción)
        self.rx_ser = serial.Serial(rx_port, baudrate, timeout=0.1)
        
        self.sequence_number = 0
        self.stats = {
            'tx_packets': 0, 'rx_packets': 0,
            'tx_bytes': 0, 'rx_bytes': 0,
            'errors': 0, 'start_time': time.time()
        }
        
        # Buffer para datos recibidos
        self.rx_buffer = []
        self.buffer_lock = threading.Lock()
        
    def set_tx_mode(self):
        GPIO.output(self.tx_control_pin, GPIO.HIGH)
        GPIO.output(self.rx_control_pin, GPIO.LOW)
        
    def set_rx_mode(self):
        GPIO.output(self.tx_control_pin, GPIO.LOW)
        GPIO.output(self.rx_control_pin, GPIO.HIGH)
    
    def calculate_checksum(self, data):
        return sum(data) & 0xFF
    
    def create_packet(self, data_value, packet_type=0x01):
        packet = bytearray()
        packet.append(packet_type)
        packet.extend(struct.pack('>H', data_value))
        packet.append(self.sequence_number & 0xFF)
        
        checksum = self.calculate_checksum(packet)
        packet.append(checksum)
        
        self.sequence_number += 1
        return packet
    
    def verify_packet(self, packet):
        if len(packet) < 5:
            return False
        
        received_checksum = packet[-1]
        calculated_checksum = self.calculate_checksum(packet[:-1])
        
        return received_checksum == calculated_checksum
    
    def transmit_data(self, data_value):
        self.set_tx_mode()
        time.sleep(0.001)  # Pequeña espera para estabilizar
        
        packet = self.create_packet(data_value)
        self.tx_ser.write(packet)
        
        self.stats['tx_packets'] += 1
        self.stats['tx_bytes'] += len(packet)
        
        self.set_rx_mode()  # Volver a modo recepción
        return packet
    
    def start_receiver(self):
        def receiver_thread():
            while True:
                if self.rx_ser.in_waiting > 0:
                    data = self.rx_ser.read(self.rx_ser.in_waiting)
                    
                    # Procesar datos recibidos
                    for byte in data:
                        # Aquí implementarías el protocolo de recepción
                        packet_data = {
                            'data': byte,
                            'timestamp': time.time(),
                            'valid': True
                        }
                        
                        with self.buffer_lock:
                            self.rx_buffer.append(packet_data)
                            self.stats['rx_packets'] += 1
                            self.stats['rx_bytes'] += 1
                
                time.sleep(0.01)
        
        thread = threading.Thread(target=receiver_thread)
        thread.daemon = True
        thread.start()
    
    def get_received_data(self, clear=True):
        with self.buffer_lock:
            data = self.rx_buffer.copy()
            if clear:
                self.rx_buffer.clear()
        return data
    
    def get_statistics(self):
        uptime = time.time() - self.stats['start_time']
        return {
            'tx_packets': self.stats['tx_packets'],
            'rx_packets': self.stats['rx_packets'],
            'tx_bytes': self.stats['tx_bytes'],
            'rx_bytes': self.stats['rx_bytes'],
            'errors': self.stats['errors'],
            'uptime': uptime,
            'tx_rate': self.stats['tx_bytes'] / uptime if uptime > 0 else 0,
            'rx_rate': self.stats['rx_bytes'] / uptime if uptime > 0 else 0
        }

# Uso del maestro full duplex
if __name__ == "__main__":
    master = RS485FullDuplexMaster()
    master.start_receiver()
    master.set_rx_mode()  # Iniciar en modo recepción
    
    try:
        counter = 0
        while True:
            # Transmitir cada 3 segundos
            if counter % 3 == 0:
                data = counter % 1000
                packet = master.transmit_data(data)
                print(f"📤 Transmitido: {data}")
            
            # Mostrar datos recibidos
            received = master.get_received_data()
            if received:
                print(f"📥 Recibidos {len(received)} paquetes")
            
            # Estadísticas cada 10 ciclos
            if counter % 10 == 0:
                stats = master.get_statistics()
                print(f"📊 Estadísticas: {stats}")
            
            counter += 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        master.tx_ser.close()
        master.rx_ser.close()
        GPIO.cleanup()