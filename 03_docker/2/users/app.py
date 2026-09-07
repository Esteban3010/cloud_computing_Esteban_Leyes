from flask import Flask
import socket

app = Flask(__name__)

@app.route("/")
def users():
    return {
        "service": "users",
        "message": "Servicio de usuarios",
	"instance": socket.gethostname()
    }

app.run(host="0.0.0.0", port=5000)
