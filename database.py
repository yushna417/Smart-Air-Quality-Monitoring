import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime

def create_db():
    conn = sqlite3.connect('dataforairquality.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS air_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_type TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, cursor

def insert_sensor_data(cursor, sensor_type, value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("INSERT INTO air_metrics (sensor_type, value, timestamp) VALUES (?, ?, ?)",
                   (sensor_type, value, timestamp))
    cursor.connection.commit()
    print(f"Data inserted: {sensor_type} = {value} at {timestamp}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor_data")
    print("Subscribed to topics: sensor_data")

def on_message(client, userdata, msg):
    sensor_type = msg.topic.split('/')[-1]
    value = str(msg.payload.decode())

    conn, cursor = create_db()
    insert_sensor_data(cursor, sensor_type, value)
    conn.close()

def setup_mqtt():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.loop_forever()

if __name__ == "__main__":
    setup_mqtt()