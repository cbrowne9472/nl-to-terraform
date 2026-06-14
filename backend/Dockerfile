FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends wget unzip && \
    wget -q https://releases.hashicorp.com/terraform/1.15.3/terraform_1.15.3_linux_amd64.zip && \
    unzip terraform_1.15.3_linux_amd64.zip -d /usr/local/bin/ && \
    rm terraform_1.15.3_linux_amd64.zip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
