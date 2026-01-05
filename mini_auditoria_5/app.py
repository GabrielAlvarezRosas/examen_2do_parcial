from flask import Flask, request, jsonify
import hashlib
import subprocess
import json
import os
import requests
 
app = Flask(__name__)
 
# ❌ Hallazgo típico: secreto hardcodeado en el código
API_TOKEN = "hardcoded-token-123"
 
@app.post("/login")
def login():
	data = request.get_json(silent=True) or {}
 
	username = data.get("username", "")
	password = data.get("password", "")
 
	# ❌ Hallazgo típico: hashing inseguro para contraseñas (MD5)
	password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
 
	# ❌ Hallazgo típico: eval de entrada (ej: filtros/params)
	# Supón que el frontend manda {"extra_filters": "{'role':'admin'}"}
	extra_filters_raw = data.get("extra_filters", "{}")
	extra_filters = eval(extra_filters_raw)  # INSEGURO
 
	# ❌ Hallazgo típico: shell=True con entrada (inyección de comando)
	host = data.get("host_to_ping", "127.0.0.1")
	ping_cmd = f"ping -c 1 {host}"
	ping_output = subprocess.check_output(ping_cmd, shell=True, text=True)
 
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
