# node-api/Dockerfile

FROM node:18-alpine (define a imagem a ser Dockerizada)

WORKDIR /usr/src/app (Define o diretório da aplicação)

COPY package*.json ./ (Copia as dependencias necessárias para rodar a aplicação em package.json)

RUN npm install (Roda o comando de intalação da dependncias)

COPY . . (Copia os outros arquivos da aplicação, pois já copiamos o package.json anteriormente)

EXPOSE 3001 (Porta em que é exposto a aplicação)

CMD ["node", "src/app.js"] (Comando para rodar a aplicação)


# python-api/Dockerfile

FROM python:3.11-slim (define a imagem a ser Dockerizada)

WORKDIR /app (Define o diretório da aplicação)

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* (Instala as dependencias do redis e do MySQL)

COPY requirements.txt . (Copia o arquivo com as dependencias da aplicação)

RUN pip install --no-cache-dir -r requirements.txt (Executa as dependencias copiadas em requirements.txt)

COPY . . (Copia os outros arquivos da aplicação, pois já copiamos o requirements.txt anteriormente)

EXPOSE 3002 (Porta em que é exposto a aplicação)

CMD ["python", "app.py"] (Comando para rodar a aplicação)


# php-api/Dockerfile

FROM php:8.2-apache (define a imagem a ser Dockerizada)

WORKDIR /var/www/html (Define o diretório da aplicação)

COPY index.php . (Copia o index.php, pois é o único arquivo no deretória, além do Dockerfile)

RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli (Instala a extensão para rodar o MySQL)

EXPOSE 80 (expõe na porta 80)

CMD ["apache2-foreground"] (Comando para rodar a aplicação)


# docker-compose.yml

version: '3.8'  (define a versão do compose)

services:   (Dentro dele é definido os serviços, com seus respectivos arquivos Docker e que compõem a aplicação)

redis:  (Serviço do rediz)
  image: redis:alpine   (Define a imagem para o Docker do redis)
  ports:
    - "6379:6379"   (Define a porta em que o redis é exposto)

db: (Serviço do banco de dados)
  image: mysql:8.0  (Define a imagem para o Docker domysql)
  environment:  (Define o ambiente do banco)
    MYSQL_ROOT_PASSWORD: example    (Define a senha do banco)
    MYSQL_DATABASE: ecommerce   (Define o nome da database)
  ports:
    - "3306:3306"   (Define a porta em que é exposto)

products:   (Serviço da api node)
    build: ./node-api   (Executa o build do dockerfile que está na rota especificada)
    ports:
      - "3001:3001"     (Define a porta do container)

orders:   (Serviço da api python)
    build: ./python-api     (Executa o build do dockerfile que está na rota especificada)
    ports:
      - "3002:3002"     (Define a porta do container)
    environment:    (Define as variáveis ambiente que são utilizadas na api)
      - REDIS_HOST=redis    (Serviço do redis)
      - PRODUCTS_API_URL=http://products:3001/products      (url da api node)
      - MYSQL_HOST=db   (Host do banco)
      - MYSQL_USER=root     (usuário do banco)
      - MYSQL_PASSWORD=example      (senha do banco)
      - MYSQL_DB=ecommerce      (nome do banco)
    depends_on:     (Define os serviços dos quais esse serviçi da api python depende)
      - db      (Serviço do banco)
      - redis       (Serviço do redis)
      - products    (Serviço da api node)

payments:   (Serviço da api php)
    build: ./php-api    (Executa o build do dockerfile que está na rota especificada)
    ports:
      - "3003:80"   (Define a porta do container)
    depends_on:     (Define os serviços dos quais esse serviçi da api php depende)
      - orders      (Serviço da api python)