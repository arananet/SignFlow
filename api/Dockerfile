FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stmc_core /app/stmc_core
RUN pip install --no-cache-dir -r /app/stmc_core/requirements.txt

COPY *.py ./

CMD sh -c "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"
