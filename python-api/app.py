from flask import Flask, jsonify
import redis
import requests
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)

# Configurações para desenvolvimento LOCAL
# Configurações Docker (usará variáveis de ambiente)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
PRODUCTS_API_URL = os.getenv('PRODUCTS_API_URL', 'http://localhost:3001/products')
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'ecommerce'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.route('/order')
def create_order():
    # Consulta produtos (com cache no Redis)
    try:
        cached_product = cache.get('product_1')
        if cached_product:
            product = eval(cached_product)
            print("Produto recuperado do cache Redis")
        else:
            print("Consultando API de produtos diretamente")
            response = requests.get(PRODUCTS_API_URL)
            response.raise_for_status()  # Verifica erros HTTP
            product = response.json()['products'][0]
            cache.setex('product_1', 30, str(product))  # Cache por 30 segundos
    except Exception as e:
        return jsonify({'error': f"Erro ao consultar produtos: {str(e)}"}), 500

    # Registra no MySQL
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor()
        
        # Cria tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                quantity INT,
                total_price INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insere pedido
        total_price = product['price'] * 2
        cursor.execute(
            "INSERT INTO orders (product_id, quantity, total_price) VALUES (%s, %s, %s)",
            (product['id'], 2, total_price)
        )
        db.commit()
        
        order_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({
            "order_id": order_id,
            "product_id": product['id'],
            "quantity": 2,
            "total_price": total_price,
            "message": "Pedido registrado com sucesso"
        })
        
    except Exception as e:
        return jsonify({'error': f"Erro no MySQL: {str(e)}"}), 500

@app.route('/debug')
def debug():
    try:
        # Teste Redis
        cache.ping()
        redis_status = "OK"
    except Exception as e:
        redis_status = f"Erro: {str(e)}"

    try:
        # Teste MySQL
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        conn.close()
        mysql_status = "OK"
    except Exception as e:
        mysql_status = f"Erro: {str(e)}"

    return jsonify({
        "redis": redis_status,
        "mysql": mysql_status,
        "products_api": PRODUCTS_API_URL,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)