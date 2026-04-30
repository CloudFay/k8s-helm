from flask import Flask, jsonify
import os
import socket
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis.k8s-helm")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def read_secret(name):
    path = f"/etc/secrets/{name}"
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.getenv(name, "not-set")

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from Kubernetes!",
        "hostname": socket.gethostname(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "env": os.getenv("APP_ENV", "unknown"),
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/secret-check")
def secret_check():
    pw = read_secret("db-password")
    return jsonify({
        "secret_loaded": pw != "not-set",
        "secret_length": len(pw)
    })

@app.route("/counter")
def counter():
    try:
        r = get_redis()
        count = r.incr("visit_count")
        return jsonify({
            "visits": count,
            "counted_by": socket.gethostname(),
            "redis_host": REDIS_HOST
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route("/dns-check")
def dns_check():
    try:
        ip = socket.gethostbyname(REDIS_HOST)
        return jsonify({
            "redis_host": REDIS_HOST,
            "resolved_ip": ip,
            "dns_working": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "dns_working": False}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)