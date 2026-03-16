FROM python:3.9-slim

#System deps for PIL/matplotlib
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY run_models.py .
ENTRYPOINT ["python", "run_models.py"]