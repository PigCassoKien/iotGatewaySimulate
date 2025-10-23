FROM python:3.9-slim
WORKDIR /app
COPY gateway.py .
RUN pip install paho-mqtt requests
CMD ["python", "gateway.py"]
