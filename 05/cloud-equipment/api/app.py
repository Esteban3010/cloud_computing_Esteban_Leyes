import os

import boto3
import psycopg2
from psycopg2 import IntegrityError
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename


app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "equipment"),
        user=os.getenv("DB_USER", "equipment"),
        password=os.getenv("DB_PASSWORD", "change-me")
    )


def equipo_to_dict(row):
    return {
        "id": row[0],
        "codigo_interno": row[1],
        "tipo": row[2],
        "marca": row[3],
        "modelo": row[4],
        "numero_serie": row[5],
        "estado": row[6],
        "fecha_adquisicion": str(row[7]) if row[7] else None,
        "empleado_id": row[8]
    }


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "equipment-api"
    })


# --------------------------------------------------
# EQUIPOS
# --------------------------------------------------

@app.get("/equipos")
def equipos():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, internal_code, type, brand, model,
               serial_number, status, acquisition_date, employee_id
        FROM equipment
        ORDER BY id;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([equipo_to_dict(row) for row in rows])


@app.post("/equipos")
def crear_equipo():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    if not data.get("codigo_interno"):
        return jsonify({"error": "codigo_interno es obligatorio"}), 400

    if not data.get("tipo"):
        return jsonify({"error": "tipo es obligatorio"}), 400

    if not data.get("estado"):
        return jsonify({"error": "estado es obligatorio"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO equipment
            (internal_code, type, brand, model, serial_number,
             status, acquisition_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            data["codigo_interno"],
            data["tipo"],
            data.get("marca"),
            data.get("modelo"),
            data.get("numero_serie"),
            data["estado"],
            data.get("fecha_adquisicion")
        ))

        equipment_id = cur.fetchone()[0]
        conn.commit()

    except IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "El código interno o número de serie ya existe"
        }), 409

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "id": equipment_id,
        "mensaje": "Equipo creado correctamente"
    }), 201


@app.get("/equipos/<int:equipment_id>")
def obtener_equipo(equipment_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, internal_code, type, brand, model,
               serial_number, status, acquisition_date, employee_id
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Equipo no encontrado"}), 404

    return jsonify(equipo_to_dict(row))


@app.put("/equipos/<int:equipment_id>")
def actualizar_equipo(equipment_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT internal_code, type, brand, model,
               serial_number, status, acquisition_date
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    equipo = cur.fetchone()

    if equipo is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Equipo no encontrado"}), 404

    try:
        cur.execute("""
            UPDATE equipment
            SET internal_code = %s,
                type = %s,
                brand = %s,
                model = %s,
                serial_number = %s,
                status = %s,
                acquisition_date = %s
            WHERE id = %s;
        """, (
            data.get("codigo_interno", equipo[0]),
            data.get("tipo", equipo[1]),
            data.get("marca", equipo[2]),
            data.get("modelo", equipo[3]),
            data.get("numero_serie", equipo[4]),
            data.get("estado", equipo[5]),
            data.get("fecha_adquisicion", equipo[6]),
            equipment_id
        ))

        conn.commit()

    except IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "El código interno o número de serie ya pertenece a otro equipo"
        }), 409

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "id": equipment_id,
        "mensaje": "Equipo actualizado correctamente"
    })


# --------------------------------------------------
# EMPLEADOS
# --------------------------------------------------

@app.get("/empleados")
def obtener_empleados():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, email, department
        FROM employees
        ORDER BY id;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    empleados = []

    for row in rows:
        empleados.append({
            "id": row[0],
            "nombre": row[1],
            "correo": row[2],
            "departamento": row[3]
        })

    return jsonify(empleados)


@app.post("/empleados")
def crear_empleado():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    if not data.get("nombre"):
        return jsonify({"error": "nombre es obligatorio"}), 400

    if not data.get("correo"):
        return jsonify({"error": "correo es obligatorio"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO employees (name, email, department)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (
            data["nombre"],
            data["correo"],
            data.get("departamento")
        ))

        empleado_id = cur.fetchone()[0]
        conn.commit()

    except IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Ya existe un empleado con ese correo"
        }), 409

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "id": empleado_id,
        "mensaje": "Empleado creado correctamente"
    }), 201


@app.get("/empleados/<int:employee_id>")
def obtener_empleado(employee_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, email, department
        FROM employees
        WHERE id = %s;
    """, (employee_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Empleado no encontrado"}), 404

    return jsonify({
        "id": row[0],
        "nombre": row[1],
        "correo": row[2],
        "departamento": row[3]
    })


# --------------------------------------------------
# ASIGNACIONES
# --------------------------------------------------

@app.post("/equipos/<int:equipment_id>/asignar")
def asignar_equipo(equipment_id):
    data = request.get_json(silent=True)

    if not data or not data.get("empleado_id"):
        return jsonify({
            "error": "empleado_id es obligatorio"
        }), 400

    empleado_id = data["empleado_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, status
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    equipo = cur.fetchone()

    if equipo is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Equipo no encontrado"}), 404

    cur.execute("""
        SELECT id
        FROM employees
        WHERE id = %s;
    """, (empleado_id,))

    empleado = cur.fetchone()

    if empleado is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Empleado no encontrado"}), 404

    if equipo[1] != "DISPONIBLE":
        cur.close()
        conn.close()
        return jsonify({
            "error": "El equipo no está disponible"
        }), 400

    cur.execute("""
        UPDATE equipment
        SET employee_id = %s,
            status = 'ASIGNADO'
        WHERE id = %s;
    """, (
        empleado_id,
        equipment_id
    ))

    cur.execute("""
        INSERT INTO assignments
        (equipment_id, employee_id)
        VALUES (%s, %s);
    """, (
        equipment_id,
        empleado_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "equipo_id": equipment_id,
        "empleado_id": empleado_id,
        "mensaje": "Equipo asignado correctamente"
    })


# --------------------------------------------------
# MANTENIMIENTOS
# --------------------------------------------------

@app.post("/equipos/<int:equipment_id>/mantenimientos")
def crear_mantenimiento(equipment_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    equipo = cur.fetchone()

    if equipo is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Equipo no encontrado"}), 404

    cur.execute("""
        INSERT INTO maintenance
        (equipment_id, type, description, cost)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (
        equipment_id,
        data.get("tipo"),
        data.get("descripcion"),
        data.get("costo")
    ))

    maintenance_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": maintenance_id,
        "equipo_id": equipment_id,
        "mensaje": "Mantenimiento registrado correctamente"
    }), 201


# --------------------------------------------------
# HISTORIAL
# --------------------------------------------------

@app.get("/equipos/<int:equipment_id>/historial")
def historial_equipo(equipment_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, internal_code, type, brand, model,
               serial_number, status, acquisition_date, employee_id
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    equipo = cur.fetchone()

    if equipo is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Equipo no encontrado"}), 404

    cur.execute("""
        SELECT a.id,
               a.assigned_at,
               e.id,
               e.name
        FROM assignments a
        JOIN employees e
          ON e.id = a.employee_id
        WHERE a.equipment_id = %s
        ORDER BY a.assigned_at;
    """, (equipment_id,))

    asignaciones = cur.fetchall()

    cur.execute("""
        SELECT id,
               maintenance_date,
               type,
               description,
               cost
        FROM maintenance
        WHERE equipment_id = %s
        ORDER BY maintenance_date;
    """, (equipment_id,))

    mantenimientos = cur.fetchall()

    cur.close()
    conn.close()

    eventos = []

    for row in asignaciones:
        eventos.append({
            "evento": "ASIGNACION",
            "id": row[0],
            "fecha": row[1].isoformat(),
            "empleado_id": row[2],
            "empleado": row[3]
        })

    for row in mantenimientos:
        eventos.append({
            "evento": "MANTENIMIENTO",
            "id": row[0],
            "fecha": row[1].isoformat(),
            "tipo": row[2],
            "descripcion": row[3],
            "costo": float(row[4]) if row[4] is not None else None
        })

    eventos.sort(key=lambda evento: evento["fecha"])

    return jsonify({
        "equipo": equipo_to_dict(equipo),
        "historial": eventos
    })


# --------------------------------------------------
# DOCUMENTOS EN S3
# --------------------------------------------------

@app.post("/equipos/<int:equipment_id>/documentos")
def subir_documento(equipment_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM equipment
        WHERE id = %s;
    """, (equipment_id,))

    equipo = cur.fetchone()

    if equipo is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Equipo no encontrado"}), 404

    if "file" not in request.files:
        cur.close()
        conn.close()
        return jsonify({
            "error": "Debe enviar un archivo en el campo file"
        }), 400

    file = request.files["file"]

    if not file.filename:
        cur.close()
        conn.close()
        return jsonify({"error": "El archivo no tiene nombre"}), 400

    file_name = secure_filename(file.filename)

    if not file_name:
        cur.close()
        conn.close()
        return jsonify({"error": "Nombre de archivo inválido"}), 400

    bucket = os.getenv("S3_BUCKET")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket:
        cur.close()
        conn.close()
        return jsonify({
            "error": "S3_BUCKET no está configurado"
        }), 500

    s3_key = f"equipos/{equipment_id}/{file_name}"

    try:
        s3 = boto3.client("s3", region_name=region)

        s3.upload_fileobj(
            file,
            bucket,
            s3_key
        )

        cur.execute("""
            INSERT INTO documents
            (equipment_id, file_name, s3_key)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (
            equipment_id,
            file_name,
            s3_key
        ))

        document_id = cur.fetchone()[0]

        conn.commit()

    except Exception as error:
        conn.rollback()

        return jsonify({
            "error": "No fue posible cargar el documento",
            "detalle": str(error)
        }), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "id": document_id,
        "equipo_id": equipment_id,
        "archivo": file_name,
        "s3_key": s3_key,
        "mensaje": "Documento cargado correctamente"
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
