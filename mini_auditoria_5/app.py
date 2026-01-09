from flask import Flask, request, jsonify
import bcrypt
import subprocess
import json
import os
import shutil
import platform
import re
import requests
 
app = Flask(__name__)
 
# ❌ Hallazgo típico: secreto hardcodeado en el código
API_TOKEN = "hardcoded-token-123"
 
@app.post("/login")
def login():
	data = request.get_json(silent=True) or {}
 
	username = data.get("username", "")
	password = data.get("password", "")
 
	# ✓ Hashing seguro para contraseñas (bcrypt)
	password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
 
	# ❌ Hallazgo típico: eval de entrada (ej: filtros/params)
	# Supón que el frontend manda {"extra_filters": "{'role':'admin'}"}
	extra_filters_raw = data.get("extra_filters", "{}")
	extra_filters = eval(extra_filters_raw)  # INSEGURO
 
	# ✓ Inyección de comando prevenida: resolve full path to `ping` and use args list
	host = data.get("host_to_ping", "127.0.0.1")
	# Basic validation: allow only letters, numbers, dot and hyphen
	if not re.match(r'^[A-Za-z0-9.\-]+$', host):
		host = "127.0.0.1"

	ping_cmd = "ping"
	ping_path = shutil.which(ping_cmd)
	if not ping_path:
		raise RuntimeError("'ping' executable not found on PATH")

	# Use platform-specific count flag: Windows uses -n, others use -c
	count_flag = "-n" if platform.system().lower().startswith("win") else "-c"
	ping_output = subprocess.check_output([ping_path, count_flag, "1", host], text=True)
 
	# ❌ Hallazgo típico: deshabilitar verificación TLS
	profile_url = data.get("profile_url", "https://example.com")
	r = requests.get(profile_url, headers={"Authorization": f"Bearer {API_TOKEN}"}, verify=False)
 
	return jsonify({
    	"user": username,
    	"password_hash": password_hash,
    	"extra_filters": extra_filters,
    	"ping": ping_output[:80],
    	"profile_status": r.status_code
	})
