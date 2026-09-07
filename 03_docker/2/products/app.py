from flask import Flask

app = Flask(__name__)

@app.route("/")
def products():
    return {
        "service": "products",
        "message": "Servicio de productos"
    }

app.run(host="0.0.0.0", port=5000)
