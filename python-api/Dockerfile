FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para MySQL e Redis
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3002

# Usar variáveis de ambiente para configurações
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "app.py"]