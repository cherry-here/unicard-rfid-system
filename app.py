"""
UNICARD -- All-in-One Vehicle Document Smart Card System
Author: Mothi Charan Naik Desavath
Hardware: Raspberry Pi + NodeMCU (ESP8266) + MFRC522 RFID
Backend: Python Flask + MySQL
Features: Role-based access, Fernet-encrypted rolling token, 4-in-1 docs
"""

# =======================================================
# app.py -- Flask Backend (Raspberry Pi)
# =======================================================

from flask import Flask, request, render_template, redirect, session, jsonify
import mysql.connector
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Database Setup -------------------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="unicard_db"
)
cursor = db.cursor(dictionary=True)

# --- Fernet Encryption Key -----------------------------
KEY_FILE = "fernet_key.key"
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        fernet = Fernet(f.read())
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    fernet = Fernet(key)


def generate_token():
    """Generate a new Fernet-encrypted rolling token with timestamp."""
    token_data = f"{os.urandom(8).hex()}:{datetime.now().isoformat()}"
    return fernet.encrypt(token_data.encode()).decode()


def validate_token(token_str):
    """Decrypt and validate rolling token (max 1 hour age)."""
    try:
        decrypted = fernet.decrypt(token_str.encode()).decode()
        token_time = datetime.fromisoformat(decrypted.split(":")[1])
        return (datetime.now() - token_time) < timedelta(hours=1)
    except:
        return False


def hash_password(password):
    """SHA-256 password hashing."""
    return hashlib.sha256(password.encode()).hexdigest()


# --- RFID Scan Endpoint (called by NodeMCU) ------------
@app.route("/nodemcu_scan", methods=["GET"])
def nodemcu_scan():
    uid = request.args.get("uid", "")
    token = request.args.get("token", "")

    cursor.execute("SELECT * FROM users WHERE rfid_uid=%s", (uid,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"status": "new_user", "url": "/register?uid=" + uid})

    if token:
        if not validate_token(token):
            return jsonify({"status": "tampered", "msg": "Token mismatch! Possible tampering"})
        # Generate new rolling token
        new_token = generate_token()
        cursor.execute("UPDATE users SET current_token=%s WHERE rfid_uid=%s", (new_token, uid))
        db.commit()
        return jsonify({"status": "ok", "url": "/login?uid=" + uid + "&token=" + new_token})
    else:
        return jsonify({"status": "ok", "url": "/login?uid=" + uid + "&token=" + user["current_token"]})


# --- Registration --------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    uid = request.args.get("uid", "")
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        license_no = request.form["license"]
        password = hash_password(request.form["password"])
        sq1 = request.form["sq1"]  # favourite food
        sq2 = request.form["sq2"]  # school name
        sq3 = request.form["sq3"]  # native place
        sq4 = request.form["sq4"]  # favourite person
        token = generate_token()

        cursor.execute(
            "INSERT INTO users (rfid_uid, name, mobile, license_no, password, "
            "sq1, sq2, sq3, sq4, current_token) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (uid, name, mobile, license_no, password, sq1, sq2, sq3, sq4, token)
        )
        db.commit()
        return redirect("/success")
    return render_template("register.html", uid=uid)


# --- User Login ----------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    uid = request.args.get("uid", "")
    token = request.args.get("token", "")
    if request.method == "POST":
        password = hash_password(request.form["password"])
        cursor.execute("SELECT * FROM users WHERE rfid_uid=%s AND password=%s", (uid, password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["role"] = "user"
            return redirect("/dashboard")
    return render_template("login.html", uid=uid, token=token)


# --- User Dashboard -------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    cursor.execute("SELECT * FROM vehicles WHERE user_id=%s", (user_id,))
    vehicles = cursor.fetchall()

    cursor.execute("SELECT * FROM insurance WHERE user_id=%s", (user_id,))
    insurance = cursor.fetchall()

    return render_template("dashboard.html", vehicles=vehicles, insurance=insurance)


# --- Stakeholder Login ---------------------------------
@app.route("/stakeholder", methods=["GET", "POST"])
def stakeholder_login():
    if request.method == "POST":
        sid = request.form["id"]
        password = hash_password(request.form["password"])
        cursor.execute("SELECT * FROM stakeholders WHERE stakeholder_id=%s AND password=%s", (sid, password))
        stakeholder = cursor.fetchone()
        if stakeholder:
            session["stakeholder_id"] = stakeholder["id"]
            session["role"] = stakeholder["role"]  # manufacturer / insurer / police
            session["company"] = stakeholder["company"]
            return redirect("/stakeholder/dashboard")
    return render_template("stakeholder_login.html")


# --- Stakeholder Dashboard -----------------------------
@app.route("/stakeholder/dashboard", methods=["GET", "POST"])
def stakeholder_dashboard():
    if "stakeholder_id" not in session:
        return redirect("/stakeholder")
    role = session["role"]

    if request.method == "POST":
        rfid_tag = request.form["rfid_tag"]

        if role == "manufacturer":
            vin = request.form["vin"]
            model = request.form["model"]
            rc_number = request.form["rc_number"]
            cursor.execute(
                "INSERT INTO vehicles (rfid_tag, vin, model, rc_number, added_by, added_date) "
                "VALUES (%s,%s,%s,%s,%s,CURDATE())",
                (rfid_tag, vin, model, rc_number, session["company"])
            )
        elif role == "insurer":
            policy_no = request.form["policy_no"]
            expiry = request.form["expiry"]
            cursor.execute(
                "INSERT INTO insurance (rfid_tag, policy_no, expiry, company) VALUES (%s,%s,%s,%s)",
                (rfid_tag, policy_no, expiry, session["company"])
            )
        db.commit()

    return render_template("stakeholder_dashboard.html", role=role, company=session["company"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)