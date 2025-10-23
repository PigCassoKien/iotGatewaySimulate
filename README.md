 git clone https://github.com/PigCassoKien/iotGatewaySimulate.git
Đảm bảo đã tải docker, kiểm tra bằng lệnh: 
docker version
1. Build và chạy container mosquitto:  (chỗ cd thay thế bằng đường dẫn thực tế) 
 cd E:\iot_nids_project\mosquitto 
 docker build -t mosquitto .
 docker run -d -p 1883:1883 --name mosquitto mosquitto
2. Build và chạy container IoT Gateway: (chỗ cd thay thế bằng đường dẫn thực tế) 
 cd E:\iot_nids_project\gateway
 docker build -t iot-gateway .
 docker run -d --name iot-gateway --network host iot-gateway
3. Build và chạy container IDS Server (chỗ cd thay thế bằng đường dẫn thực tế) 
 cd E:\iot_nids_project\ids_server
 docker build -t ids-server .
 docker run -d -p 5000:5000 --name ids-server --network host ids-server
4. Chạy esp32 giả lập (chỗ cd thay thế bằng đường dẫn thực tế) 
  cd E:\iot_nids_project\simulate_esp32
 python simulate_esp32.py
5. Thay thế esp32 giả lập bằng esp32 thực tế, cái này hỏi chatGpt thử xem chứ t cũng chưa có mạch để thử bao h 
6. Cài đặt và cấu hình Mosquitto MQTT Broker thực tế (cũng thử hỏi ChatGpt xem sao)
https://grok.com/share/bGVnYWN5_e19616cf-10cf-459f-9b1a-2a32f9cc889f
Thử tham khảo cái này xem