FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt  # Add if you have deps
ENTRYPOINT ["python", "app.py"]  # Or your main script