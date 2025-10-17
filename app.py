import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

# -------------------------------
# 🔹 Configuración inicial
# -------------------------------
st.set_page_config(page_title="Control MQTT", page_icon="📡", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #e9edc9;
        color: #3a3a3a;
        font-family: 'Segoe UI';
    }
    .stButton>button {
        background-color: #52796f;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #354f52;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 Control MQTT")
st.write("Versión de Python:", platform.python_version())

# -------------------------------
# 🔹 Parámetros del broker
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuración MQTT")
    broker = st.text_input("Broker MQTT", "broker.mqttdashboard.com")
    port = st.number_input("Puerto", 1883)
    topic_control = st.text_input("Tópico de control", "cmqtt_s")
    topic_sensor = st.text_input("Tópico de sensores", "Sensores")

# -------------------------------
# 🔹 Estado inicial
# -------------------------------
if "mqtt_client" not in st.session_state:
    st.session_state.mqtt_client = None
if "connected" not in st.session_state:
    st.session_state.connected = False
if "log" not in st.session_state:
    st.session_state.log = []
if "last_message" not in st.session_state:
    st.session_state.last_message = "Ningún mensaje recibido aún."

placeholder_msg = st.empty()

# -------------------------------
# 🔹 Funciones de callback MQTT
# -------------------------------
def on_publish(client, userdata, result):
    log_event("📤 Mensaje publicado correctamente.")

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    st.session_state.last_message = f"📩 Mensaje recibido: `{data}`"
    placeholder_msg.write(st.session_state.last_message)
    log_event(f"Mensaje recibido: {data}")

def log_event(event):
    st.session_state.log.append(f"{time.strftime('%H:%M:%S')} - {event}")

# -------------------------------
# 🔹 Inicializar conexión MQTT persistente
# -------------------------------
def connect_mqtt():
    try:
        client = paho.Client("Streamlit-MQTT")
        client.on_message = on_message
        client.on_publish = on_publish
        client.connect(broker, int(port))
        client.loop_start()
        st.session_state.mqtt_client = client
        st.session_state.connected = True
        log_event("Conectado al broker MQTT ✅")
        st.success("Conectado exitosamente al broker ✅")
    except Exception as e:
        st.session_state.connected = False
        st.error(f"Error al conectar con el broker: {e}")
        log_event(f"❌ Error al conectar: {e}")

if st.button("🔌 Conectar al Broker"):
    connect_mqtt()

# -------------------------------
# 🔹 Botones principales
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("ON"):
        if st.session_state.connected:
            msg = json.dumps({"Act1": "ON"})
            st.session_state.mqtt_client.publish(topic_control, msg)
            log_event("Act1 enviado: ON")
        else:
            st.warning("Conéctate primero al broker MQTT.")

with col2:
    if st.button("OFF"):
        if st.session_state.connected:
            msg = json.dumps({"Act1": "OFF"})
            st.session_state.mqtt_client.publish(topic_control, msg)
            log_event("Act1 enviado: OFF")
        else:
            st.warning("Conéctate primero al broker MQTT.")

with col3:
    if st.button("Suscribirse a Sensores"):
        if st.session_state.connected:
            st.session_state.mqtt_client.subscribe(topic_sensor)
            log_event(f"Suscrito al tópico: {topic_sensor}")
            st.success(f"Suscrito a '{topic_sensor}' ✅")
        else:
            st.warning("Conéctate primero al broker MQTT.")

# -------------------------------
# 🔹 Control de valor analógico
# -------------------------------
values = st.slider('Selecciona el valor analógico', 0.0, 100.0, 50.0)
if st.button("Enviar valor analógico"):
    if st.session_state.connected:
        msg = json.dumps({"Analog": float(values)})
        st.session_state.mqtt_client.publish("cmqtt_a", msg)
        log_event(f"Valor analógico enviado: {values}")
    else:
        st.warning("Conéctate primero al broker MQTT.")

# -------------------------------
# 🔹 Mostrar estado y logs
# -------------------------------
st.divider()
st.subheader("📜 Último mensaje recibido")
st.write(st.session_state.last_message)

st.subheader("🧾 Registro de eventos")
st.text_area("Eventos", "\n".join(st.session_state.log), height=200)
