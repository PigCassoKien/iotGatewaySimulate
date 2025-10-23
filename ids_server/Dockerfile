FROM python:3.9-slim
WORKDIR /app
COPY app.py .
COPY templates/ templates/
RUN pip install flask scikit-learn numpy
CMD ["python", "app.py"]