import paho.mqtt.client as mqtt
import json
import requests
import hashlib
import time

broker = 'localhost'
port = 1883
topic_data = 'iot/sensor/data'
topic_response = 'iot/response'

# Lưu trữ dữ liệu mới nhất từ mỗi thiết bị
latest_data = {
    'esp32_dht': None,
    'esp32_mq2': None
}

def validate_checksum(data):
    received_checksum = data.pop('checksum', None)
    calculated_checksum = int(hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:2], 16)
    return received_checksum == calculated_checksum

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'Connected to MQTT with code {reason_code}')
        client.subscribe(topic_data)
    else:
        print(f'Connection failed with code {reason_code}')

def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        print(f'Received: {data}')

        # Security Layer: Xác thực thiết bị
        valid_devices = ['esp32_dht', 'esp32_mq2']
        if data['dev_id'] not in valid_devices:
            print(f'Invalid device ID: {data["dev_id"]}')
            return

        # Processing Layer: Kiểm tra checksum
        if not validate_checksum(data.copy()):
            print(f'Checksum validation failed for {data["dev_id"]}')
            return

        # Lưu dữ liệu mới nhất
        latest_data[data['dev_id']] = data

        # Kiểm tra xem có dữ liệu từ cả hai thiết bị chưa
        if all(latest_data[dev_id] is not None for dev_id in valid_devices):
            # Processing Layer: Gộp dữ liệu
            aggregated_data = {
                'timestamp': max(latest_data['esp32_dht']['timestamp'], latest_data['esp32_mq2']['timestamp']),
                'temperature': latest_data['esp32_dht']['temperature'],
                'humidity': latest_data['esp32_dht']['humidity'],
                'gas_level': latest_data['esp32_mq2']['gas_level'],
                'rssi': latest_data['esp32_mq2']['rssi'],
                'wifi_status': latest_data['esp32_mq2']['wifi_status'],
                'ssid': latest_data['esp32_mq2']['ssid'],
                'dev_ip_dht': latest_data['esp32_dht']['dev_ip'],
                'dev_ip_mq2': latest_data['esp32_mq2']['dev_ip'],
                'packet_count_dht': latest_data['esp32_dht']['packet_count'],
                'packet_count_mq2': latest_data['esp32_mq2']['packet_count'],
                'packet_interval': latest_data['esp32_dht']['packet_interval'],  # Giống nhau cho cả hai
                'dev_status_dht': latest_data['esp32_dht']['dev_status'],
                'dev_status_mq2': latest_data['esp32_mq2']['dev_status'],
                'seq_num_dht': latest_data['esp32_dht']['seq_num'],
                'seq_num_mq2': latest_data['esp32_mq2']['seq_num']
            }
            print(f'Aggregated data to send to IDS Server: {aggregated_data}')

            # Application Layer: Gửi dữ liệu tới IDS Server
            try:
                response = requests.post('http://localhost:5000/analyze', json=aggregated_data, timeout=5)
                response_data = response.json()
                print(f'IDS response: {response_data}')

                # Application Layer: Publish phản hồi về ESP
                for dev_id in valid_devices:
                    response_data['dev_id'] = dev_id
                    client.publish(topic_response, json.dumps(response_data))
                    print(f'Published to {topic_response} for {dev_id}: {response_data}')
            except requests.RequestException as e:
                print(f'Failed to send to IDS Server: {e}')

            # Reset dữ liệu sau khi gửi
            latest_data['esp32_dht'] = None
            latest_data['esp32_mq2'] = None

    except Exception as e:
        print(f'Error processing message: {e}')

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port)
client.loop_forever()