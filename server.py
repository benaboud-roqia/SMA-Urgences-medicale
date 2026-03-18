"""
Serveur Flask - Dashboard SMA Urgences Medicales
"""
import subprocess
import threading
import queue
import json
import sys
import os
import time

from flask import Flask, Response, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

log_queue = queue.Queue()
sim_running = False
sim_proc = None

PYTHON = sys.executable
MAIN_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def kill_port_5222():
    try:
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        pids = set()
        for line in result.stdout.splitlines():
            if ":5222" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    pids.add(parts[-1])
        for pid in pids:
            try:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
            except Exception:
                pass
    except Exception:
        pass


def _pipe_reader(pipe, label=""):
    """Lit un pipe ligne par ligne et pousse dans log_queue."""
    try:
        for raw in iter(pipe.readline, b""):
            try:
                line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
            except Exception:
                line = repr(raw)
            if line.strip():
                log_queue.put(line)
    except Exception:
        pass
    finally:
        pipe.close()


def _watcher_thread(proc):
    global sim_running
    proc.wait()
    sim_running = False
    log_queue.put("__STATUS__:stopped")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/start", methods=["POST"])
def start_sim():
    global sim_running, sim_proc
    if sim_running:
        return jsonify({"status": "already_running"})

    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except Exception:
            pass

    if sim_proc and sim_proc.poll() is None:
        sim_proc.terminate()
        try:
            sim_proc.wait(timeout=3)
        except Exception:
            pass

    kill_port_5222()
    time.sleep(0.8)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    sim_proc = subprocess.Popen(
        [PYTHON, "-u", MAIN_PY],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR,
        env=env,
    )
    sim_running = True
    log_queue.put("__STATUS__:running")

    threading.Thread(target=_pipe_reader, args=(sim_proc.stdout, "OUT"), daemon=True).start()
    threading.Thread(target=_pipe_reader, args=(sim_proc.stderr, "ERR"), daemon=True).start()
    threading.Thread(target=_watcher_thread, args=(sim_proc,), daemon=True).start()

    return jsonify({"status": "started"})


@app.route("/api/stop", methods=["POST"])
def stop_sim():
    global sim_running, sim_proc
    sim_running = False
    if sim_proc and sim_proc.poll() is None:
        sim_proc.terminate()
    log_queue.put("__STATUS__:stopped")
    return jsonify({"status": "stopped"})


@app.route("/api/status")
def status():
    return jsonify({"running": sim_running})


@app.route("/api/stream")
def stream():
    def generate():
        while True:
            try:
                msg = log_queue.get(timeout=20)
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                yield 'data: "__PING__"\n\n'
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    print("Serveur demarre sur http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)