import paho.mqtt.client as mqtt
import time
import json
import hashlib
from random import uniform, randint

broker = 'localhost'
port = 1883
topic_data = 'iot/sensor/data'
topic_response = 'iot/response'

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'[{client._client_id.decode()}] Connected to MQTT with code {reason_code}')
        client.subscribe(topic_response)
    else:
        print(f'[{client._client_id.decode()}] Connection failed with code {reason_code}')

def on_message(client, userdata, message):
    if message.topic == topic_response:
        data = json.loads(message.payload.decode())
        dev_id = client._client_id.decode()
        status = data['status']
        print(f'[{dev_id}] Received response: {status}')
        if dev_id == 'esp32_mq2' and status == 'attack':
            print(f'[{dev_id}] Activating LED/Buzzer')

def simulate_device(dev_id, dev_ip, sensor_type):
    client = mqtt.Client(client_id=dev_id, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    seq_num = 0

    client.loop_start()

    while True:
        data = {
            'dev_id': dev_id,  # String, 8 byte
            'timestamp': int(time.time()),  # uint32_t, 4 byte
            'dev_ip': dev_ip,  # String, 15 byte
            'packet_count': seq_num,  # uint16_t, 2 byte
            'packet_interval': 3,  # uint16_t, 2 byte
            'dev_status': 'normal',  # String, 8 byte
            'seq_num': seq_num  # uint16_t, 2 byte
        }
        if sensor_type == 'dht':
            data['temperature'] = round(uniform(20.0, 30.0), 2)  # float, 4 byte
            data['humidity'] = round(uniform(40.0, 60.0), 2)  # float, 4 byte
        elif sensor_type == 'mq2':
            data['gas_level'] = randint(100, 500)  # uint16_t, 2 byte
            data['rssi'] = randint(-80, -50)  # int8_t, 1 byte
            data['wifi_status'] = 'active'  # String, 8 byte
            data['ssid'] = 'IoT_NIDS'  # String, 15 byte
        # Tính checksum (lấy byte đầu tiên của MD5 hash)
        data_copy = data.copy()
        checksum_str = hashlib.md5(json.dumps(data_copy, sort_keys=True).encode()).hexdigest()
        data['checksum'] = int(checksum_str[:2], 16)  # uint8_t, 1 byte

        client.publish(topic_data, json.dumps(data))
        print(f'[{dev_id}] Sent: {data}')
        seq_num = (seq_num + 1) % 65536  # Giới hạn uint16_t
        time.sleep(3)

    client.loop_stop()

if __name__ == '__main__':
    devices = [
        ('esp32_dht', '192.168.4.100', 'dht'),
        ('esp32_mq2', '192.168.4.1', 'mq2')
    ]
    import threading
    for dev_id, dev_ip, sensor_type in devices:
        threading.Thread(target=simulate_device, args=(dev_id, dev_ip, sensor_type), daemon=True).start()
    while True:
        time.sleep(1)