import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector

# Load .env
load_dotenv()

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# DB config dari env (online)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "sql12.freesqldatabase.com"),
    "user": os.getenv("DB_USER", "sql12794973"),
    "password": os.getenv("DB_PASS", "jFV1KerrqA"),
    "database": os.getenv("DB_NAME", "sql12794973"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# Koneksi DB
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Buat tabel kalau belum ada
def init_db():
    sql = """
    CREATE TABLE IF NOT EXISTS servis (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tanggal DATE NOT NULL,
        nama VARCHAR(120) NOT NULL,
        kontak VARCHAR(120),
        tipe VARCHAR(20),
        merek_model VARCHAR(160),
        keluhan TEXT,
        status VARCHAR(50),
        estimasi_biaya DECIMAL(12,2) DEFAULT 0,
        biaya_real DECIMAL(12,2) DEFAULT 0,
        dp DECIMAL(12,2) DEFAULT 0,
        sisa DECIMAL(12,2) DEFAULT 0,
        catatan VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("init_db error:", e)

# Helper: ubah row ke dict
def row_to_dict(row, cols):
    return {cols[i][0]: row[i] for i in range(len(row))}

# --------- ROUTES ---------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/servis", methods=["GET"])
def list_servis():
    keyword = request.args.get("keyword", "").strip()
    tipe = request.args.get("tipe", "")
    status = request.args.get("status", "")

    base = "SELECT id, tanggal, nama, kontak, tipe, merek_model, keluhan, status, estimasi_biaya, biaya_real, dp, sisa, catatan FROM servis"
    where = []
    params = []

    if keyword:
        like = f"%{keyword}%"
        where.append("(nama LIKE %s OR kontak LIKE %s OR merek_model LIKE %s OR keluhan LIKE %s OR catatan LIKE %s)")
        params.extend([like]*5)
    if tipe and tipe != "Semua":
        where.append("tipe = %s")
        params.append(tipe)
    if status and status != "Semua":
        where.append("status = %s")
        params.append(status)

    if where:
        base += " WHERE " + " AND ".join(where)
    base += " ORDER BY id DESC"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(base, tuple(params))
    rows = cur.fetchall()
    cols = cur.description
    cur.close()
    conn.close()

    data = [row_to_dict(r, cols) for r in rows]
    for d in data:
        for k in ("estimasi_biaya","biaya_real","dp","sisa"):
            if k in d and d[k] is not None:
                d[k] = float(d[k])
    return jsonify(data)

@app.route("/api/servis", methods=["POST"])
def create_servis():
    body = request.json if request.is_json else request.form
    try:
        tanggal = body.get("tanggal") or datetime.now().strftime("%Y-%m-%d")
        nama = body.get("nama","").strip()
        if not nama:
            return jsonify({"error":"field 'nama' wajib"}), 400
        kontak = body.get("kontak","").strip()
        tipe = body.get("tipe","").strip()
        merek_model = body.get("merek_model","").strip()
        keluhan = body.get("keluhan","").strip()
        status = body.get("status","Masuk").strip()
        estimasi_biaya = float(body.get("estimasi_biaya") or 0)
        biaya_real = float(body.get("biaya_real") or 0)
        dp = float(body.get("dp") or 0)
        dasar = biaya_real if biaya_real > 0 else estimasi_biaya
        sisa = max(dasar - dp, 0.0)
        catatan = body.get("catatan","").strip()

        sql = """INSERT INTO servis (tanggal,nama,kontak,tipe,merek_model,keluhan,status,estimasi_biaya,biaya_real,dp,sisa,catatan)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        vals = (tanggal,nama,kontak,tipe,merek_model,keluhan,status,estimasi_biaya,biaya_real,dp,sisa,catatan)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({"id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/servis/<int:row_id>", methods=["PUT"])
def update_servis(row_id):
    body = request.json
    if not body:
        return jsonify({"error":"JSON body required"}), 400
    allowed = ["tanggal","nama","kontak","tipe","merek_model","keluhan","status","estimasi_biaya","biaya_real","dp","sisa","catatan"]
    sets = []
    vals = []
    for k in allowed:
        if k in body:
            val = body[k]
            if k in ("estimasi_biaya","biaya_real","dp","sisa"):
                try:
                    val = float(val)
                except:
                    val = 0.0
            sets.append(f"{k}=%s")
            vals.append(val)
    if not sets:
        return jsonify({"error":"No updatable fields provided"}), 400
    vals.append(row_id)
    sql = f"UPDATE servis SET {', '.join(sets)} WHERE id=%s"
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, tuple(vals))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/servis/<int:row_id>", methods=["DELETE"])
def delete_servis(row_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM servis WHERE id=%s", (row_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# init
if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))  # pakai 5000, bukan 3306
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG","0") == "1")
