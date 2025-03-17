from machine import Pin, I2C, ADC
import dht
from bmp180_lib import BMP180
import time
from mq135 import MQ135
#

# Initialize the sensors
mq135_sensor = MQ135(adc_pin=34)
dht_sensor = dht.DHT11(Pin(15))
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
bmp = BMP180(i2c)
pm_sensor_pin = ADC(Pin(35))
pm_sensor_pin.atten(ADC.ATTN_11DB)  

# Function to read DHT11
def call_dht():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature(), dht_sensor.humidity()
    except Exception as e:
        print("DHT11 Error:", e)
        return None, None

# Function to read BMP180
def call_bmp180():
    try:
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()
        return pressure, altitude
    except Exception as e:
        print("BMP180 Error:", e)
        return None, None

# Function to calculate PM concentration
def calculate_pm(adc_value):
    voltage = adc_value * 3.3 / 4095
    return voltage * 50 

# Function to categorize air quality
def get_air_quality_category(pm_value):
    if pm_value <= 12:
        return "Good"
    elif pm_value <= 35.4:
        return "Moderate"
    elif pm_value <= 55.4:
        return "Unhealthy for Sensitive Groups"
    elif pm_value <= 150.4:
        return "Unhealthy"
    elif pm_value <= 250.4:
        return "Very Unhealthy"
    else:
        return "Hazardous"

# Function to read all sensors
def read_all_sensors():
    temp, hum = call_dht()
    pressure, altitude = call_bmp180()
    analog_value = mq135_sensor.read_sensor()
    rs = mq135_sensor.calculate_rs(analog_value)
    gas_concentrations = {
        gas: mq135_sensor.get_gas_concentration(gas, rs)
        for gas in mq135_sensor.GAS_CURVES
    }
    pm_density = calculate_pm(pm_sensor_pin.read())
    air_quality = get_air_quality_category(pm_density)

    return {
        "temperature": temp,
        "humidity": hum,
        "pressure": pressure,
        "altitude": altitude,
        "gas_concentrations": gas_concentrations,
        "pm_density": pm_density,
        "air_quality": air_quality,
    }

# Main loop to read and print sensor data
while True:
    data = read_all_sensors()
    if data:
        print(f"DHT11 - Temperature: {data['temperature']} °C, Humidity: {data['humidity']} %")
        print(f"BMP180 - Pressure: {data['pressure']} Pa, Altitude: {data['altitude']} m")
        print("MQ-135 - Gas Concentrations (ppm):")
        for gas, value in data["gas_concentrations"].items():
            print(f"  {gas}: {value:.2f} ppm")
        print(f"PM Sensor - PM Density: {data['pm_density']:.2f} µg/m³, Air Quality: {data['air_quality']}")
        print("-" * 30)
    time.sleep(2)


