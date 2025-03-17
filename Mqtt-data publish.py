from machine import Pin, I2C, ADC
import dht
import time
import network
from umqtt.simple import MQTTClient
from bmp180_lib import BMP180
from mq135 import MQ135
import json

# MQTT parameters
mqtt_broker_ip = "192.168.254.9"
mqtt_port = 1883
mqtt_client_id = "esp32_sensor_client"
mqtt_topic = "sensor_data"

# Set up Wi-Fi connection
wifi_ssid = "Sayam@ClassicTech"
wifi_password = "S@yam2.4G"

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifi_ssid, wifi_password)

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected:", wifi.ifconfig())

# Initialize sensors
mq135_sensor = MQ135(adc_pin=34)
dht_sensor = dht.DHT11(Pin(15))
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
bmp = BMP180(i2c)
pm_sensor_pin = ADC(Pin(35))
pm_sensor_pin.atten(ADC.ATTN_11DB)

def call_dht():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature(), dht_sensor.humidity()
    except Exception as e:
        print("DHT11 Error:", e)
        return None, None

def call_bmp180():
    try:
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()
        return pressure, altitude
    except Exception as e:
        print("BMP180 Error:", e)
        return None, None

def calculate_pm(adc_value):
    voltage = adc_value * 3.3 / 4095
    return voltage * 50

def read_mq135_gases(sensor):
    try:
        analog_value = sensor.read_sensor()
        rs = sensor.calculate_rs(analog_value)
        co2 = sensor.get_gas_concentration("CO2", rs)
        co = sensor.get_gas_concentration("CO", rs)
        nh3 = sensor.get_gas_concentration("NH3", rs)
        nox = sensor.get_gas_concentration("NOx", rs)
        benzene = sensor.get_gas_concentration("Benzene", rs)
        return co2, co, nh3, nox, benzene
    except Exception as e:
        print("MQ135 Error:", e)
        return None, None, None, None, None

def read_all_sensors():
    temp, hum = call_dht()
    pressure, altitude = call_bmp180()
    co2, co, nh3, nox, benzene = read_mq135_gases(mq135_sensor)
    pm_density = calculate_pm(pm_sensor_pin.read())

    return {
        "temperature": temp,
        "humidity": hum,
        "pressure": pressure,
        "altitude": altitude,
        "co2": co2,
        "co": co,
        "nh3": nh3,
        "nox": nox,
        "benzene": benzene,
        "pm_density": pm_density,
    }

# Initialize MQTT client
mqtt_client = MQTTClient(mqtt_client_id, mqtt_broker_ip, mqtt_port)
mqtt_client.connect()

while True:
    data = read_all_sensors()
    if data:
        payload = json.dumps(data)
        mqtt_client.publish(mqtt_topic, payload)
        print(f"Published data: {payload}")
    time.sleep(2)


