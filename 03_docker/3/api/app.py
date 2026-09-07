from flask import Flask, request
import psycopg
import os

app = Flask(__name__)


def conectar_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# GET - Obtener todos los productos
@app.route("/products", methods=["GET"])
def get_products():

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, name, price FROM products")

    datos = cursor.fetchall()

    productos = []

    for producto in datos:
        productos.append({
            "id": producto[0],
            "name": producto[1],
            "price": float(producto[2])
        })

    cursor.close()
    conexion.close()

    return {
        "served_by": os.getenv("INSTANCE"),
        "products": productos
    }


# GET - Obtener un producto por ID
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id, name, price FROM products WHERE id = %s",
        (id,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if producto is None:
        return {"error": "Producto no encontrado"}, 404

    return {
        "served_by": os.getenv("INSTANCE"),
        "product": {
            "id": producto[0],
            "name": producto[1],
            "price": float(producto[2])
        }
    }


# POST - Crear producto
@app.route("/products", methods=["POST"])
def create_product():

    datos = request.get_json()

    name = datos["name"]
    price = datos["price"]

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, price)
        VALUES (%s, %s)
        RETURNING id
        """,
        (name, price)
    )

    nuevo_id = cursor.fetchone()[0]

    conexion.commit()

    cursor.close()
    conexion.close()

    return {
        "served_by": os.getenv("INSTANCE"),
        "message": "Producto creado",
        "id": nuevo_id
    }, 201


# PUT - Modificar producto
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):

    datos = request.get_json()

    name = datos["name"]
    price = datos["price"]

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name = %s, price = %s
        WHERE id = %s
        """,
        (name, price, id)
    )

    conexion.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()

        return {"error": "Producto no encontrado"}, 404

    cursor.close()
    conexion.close()

    return {
        "served_by": os.getenv("INSTANCE"),
        "message": "Producto actualizado"
    }


# DELETE - Eliminar producto
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (id,)
    )

    conexion.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()

        return {"error": "Producto no encontrado"}, 404

    cursor.close()
    conexion.close()

    return {
        "served_by": os.getenv("INSTANCE"),
        "message": "Producto eliminado"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
