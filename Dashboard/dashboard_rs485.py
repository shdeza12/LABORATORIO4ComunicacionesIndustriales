# dashboard_rs485.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
import random
from datetime import datetime

st.set_page_config(
    page_title="Monitor RS485 Simplex/Full Duplex",
    layout="wide"
)

st.title("🔌 Monitor RS485: Simplex vs Full Duplex")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")
mode = st.sidebar.radio("Modo de Comunicación", ["Simplex", "Full Duplex"])
update_interval = st.sidebar.slider("Intervalo (ms)", 100, 2000, 500)

# Simulador de datos
class DataSimulator:
    def __init__(self):
        self.simplex_data = []
        self.duplex_data = []
        self.start_time = time.time()
    
    def generate_simplex_data(self):
        return {
            'timestamp': datetime.now(),
            'data': random.randint(0, 1000),
            'sequence': len(self.simplex_data),
            'type': 'TX',  # Solo transmisión
            'mode': 'Simplex'
        }
    
    def generate_duplex_data(self):
        tx_data = {
            'timestamp': datetime.now(),
            'data': random.randint(0, 1000),
            'sequence': len(self.duplex_data),
            'type': 'TX',
            'mode': 'Full Duplex'
        }
        
        rx_data = {
            'timestamp': datetime.now(),
            'data': random.randint(0, 1000),
            'sequence': len(self.duplex_data),
            'type': 'RX', 
            'mode': 'Full Duplex'
        }
        
        return tx_data, rx_data

simulator = DataSimulator()

# Contenedores principales
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Datos en Tiempo Real")
    
    # Gráfico principal
    placeholder = st.empty()

with col2:
    st.subheader("📊 Métricas de Rendimiento")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("Paquetes TX", "156", "+12")
    
    with metric_col2:
        st.metric("Paquetes RX", "148" if mode == "Full Duplex" else "0", 
                 "+8" if mode == "Full Duplex" else "0")
    
    with metric_col3:
        st.metric("Tasa Error", "0.8%", "-0.2%")

# Actualización en tiempo real
while True:
    # Generar nuevos datos según el modo
    if mode == "Simplex":
        new_data = simulator.generate_simplex_data()
        simulator.simplex_data.append(new_data)
        df = pd.DataFrame(simulator.simplex_data[-20:])  # Últimos 20 puntos
    else:
        tx_data, rx_data = simulator.generate_duplex_data()
        simulator.duplex_data.extend([tx_data, rx_data])
        df = pd.DataFrame(simulator.duplex_data[-40:])
    
    # Crear gráfico
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=['Datos Transmitidos/Recibidos', 'Secuencia de Paquetes'])
    
    if mode == "Simplex":
        # Solo datos TX
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['data'],
                mode='lines+markers',
                name='TX Data',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
    else:
        # Datos TX y RX
        tx_df = df[df['type'] == 'TX']
        rx_df = df[df['type'] == 'RX']
        
        fig.add_trace(
            go.Scatter(
                x=tx_df['timestamp'],
                y=tx_df['data'],
                mode='lines+markers',
                name='TX Data',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=rx_df['timestamp'],
                y=rx_df['data'],
                mode='lines+markers',
                name='RX Data',
                line=dict(color='red')
            ),
            row=1, col=1
        )
    
    # Gráfico de secuencia
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['sequence'],
            mode='lines+markers',
            name='Secuencia',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True)
    
    # Actualizar gráfico
    with placeholder.container():
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar datos recientes
        st.subheader("📋 Últimos Paquetes")
        st.dataframe(df.tail(5), use_container_width=True)
    
    time.sleep(update_interval / 1000)