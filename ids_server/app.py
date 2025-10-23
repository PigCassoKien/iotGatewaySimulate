from flask import Flask, request, jsonify, render_template
import time
import json
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)
sensor_data = []
kmeans = KMeans(n_clusters=2, random_state=0)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Ngưỡng đơn giản
        status = 'normal'
        gas_level = data.get('gas_level', 0)
        rssi = data.get('rssi', 0)
        packet_count_dht = data.get('packet_count_dht', 0)
        packet_count_mq2 = data.get('packet_count_mq2', 0)
        if gas_level > 400 or rssi < -75 or packet_count_dht > 1000 or packet_count_mq2 > 1000:
            status = 'attack'

        # ML: Chuẩn bị dữ liệu
        features = [
            data.get('temperature', 0),
            data.get('humidity', 0),
            gas_level,
            rssi
        ]
        sensor_data.append({
            'timestamp': data['timestamp'],
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'gas_level': data.get('gas_level'),
            'rssi': data.get('rssi'),
            'wifi_status': data.get('wifi_status'),
            'ssid': data.get('ssid'),
            'dev_ip_dht': data.get('dev_ip_dht'),
            'dev_ip_mq2': data.get('dev_ip_mq2'),
            'packet_count_dht': packet_count_dht,
            'packet_count_mq2': packet_count_mq2,
            'packet_interval': data.get('packet_interval'),
            'dev_status_dht': data.get('dev_status_dht'),
            'dev_status_mq2': data.get('dev_status_mq2'),
            'seq_num_dht': data.get('seq_num_dht'),
            'seq_num_mq2': data.get('seq_num_mq2'),
            'status': status
        })

        # Huấn luyện KMeans nếu có đủ dữ liệu
        if len(sensor_data) > 10:
            X = np.array([[d['temperature'] or 0, d['humidity'] or 0, d['gas_level'] or 0, d['rssi'] or 0] for d in sensor_data[-100:]])
            kmeans.fit(X)
            cluster = kmeans.predict([features])[0]
            if cluster == 1:  # Giả sử cluster 1 là bất thường
                status = 'attack'

        response = {
            'timestamp': data['timestamp'],
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'gas_level': data.get('gas_level'),
            'rssi': data.get('rssi'),
            'wifi_status': data.get('wifi_status'),
            'ssid': data.get('ssid'),
            'dev_ip_dht': data.get('dev_ip_dht'),
            'dev_ip_mq2': data.get('dev_ip_mq2'),
            'packet_count_dht': packet_count_dht,
            'packet_count_mq2': packet_count_mq2,
            'packet_interval': data.get('packet_interval'),
            'dev_status_dht': data.get('dev_status_dht'),
            'dev_status_mq2': data.get('dev_status_mq2'),
            'seq_num_dht': data.get('seq_num_dht'),
            'seq_num_mq2': data.get('seq_num_mq2'),
            'status': status
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def dashboard():
    display_data = sensor_data[-10:]  # Lấy 10 bản ghi mới nhất
    return render_template('dashboard.html', data=display_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)