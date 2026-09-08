from core.Telemetry.engine import TelemetryEngine
from core.Telemetry.process_analyzer import get_process
from flask import Flask,jsonify
import time
import requests
import platform
import threading
API_URL = "https://helios-observability.onrender.com/api/metrics/telemetry"
machine_id = platform.node()
app=Flask(__name__)

@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/identity",methods=["GET"])
def identity():
    return jsonify({
        "machine_id":machine_id
    })
def run_server():
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
def run_agent():
    while True:
        telemetry=TelemetryEngine.capture_frame()
        processes=get_process(limit=10)    
        telemetry["processes"]=processes
        telemetry["machine_id"]=machine_id
        print(
            f"[HELIOS] Sending telemetry | "
            f"Machine: {machine_id} | "
            f"CPU: {telemetry['cpu']['cpu_usage']}% | "
            f"RAM: {telemetry['ram']['percent']}% | "
            f"Processes: {len(processes)}"
        )
        try:
            response=requests.post(API_URL,json=telemetry,timeout=30)
            print("Status code:", response.status_code)
            print("Server response:", response.text)
        except requests.exceptions.RequestException as e:
            print("Could not send teh telmentry engine data ",e)
        time.sleep(2)

if __name__=="__main__":
    server_thread=threading.Thread(target=run_server,daemon=True)
    server_thread.start()
    run_agent()