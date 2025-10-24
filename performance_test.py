
# performance_test.py
import time
import statistics

def test_simplex_performance(master, num_packets=100):
    start_time = time.time()
    successes = 0
    
    for i in range(num_packets):
        try:
            master.transmit_data(i)
            successes += 1
        except Exception as e:
            print(f"Error en paquete {i}: {e}")
        
        time.sleep(0.01)  # Pequeña pausa
    
    total_time = time.time() - start_time
    success_rate = (successes / num_packets) * 100
    
    print(f"🔹 Simplex - Paquetes: {num_packets}, Tiempo: {total_time:.2f}s")
    print(f"   Tasa éxito: {success_rate:.1f}%")
    print(f"   Throughput: {num_packets/total_time:.1f} pkt/s")

def test_duplex_performance(master, num_packets=100):
    start_time = time.time()
    tx_successes = 0
    rx_count = 0
    
    for i in range(num_packets):
        try:
            master.transmit_data(i)
            tx_successes += 1
        except Exception as e:
            print(f"Error TX en paquete {i}: {e}")
        
        # Contar recepciones
        rx_data = master.get_received_data()
        rx_count += len(rx_data)
        
        time.sleep(0.01)
    
    total_time = time.time() - start_time
    tx_success_rate = (tx_successes / num_packets) * 100
    
    print(f"🔸 Full Duplex - Paquetes: {num_packets}, Tiempo: {total_time:.2f}s")
    print(f"   TX éxito: {tx_success_rate:.1f}%")
    print(f"   RX recibidos: {rx_count}")
    print(f"   Throughput: {num_packets/total_time:.1f} pkt/s")
