'''
Create a blueprint in a separate module.
Define routes inside that blueprint.
Register the blueprint in the main application.

'''

from flask import Blueprint,jsonify
from flask import request
from core.serializer import TelemetrySeralize
from database.database import save_metric
from database.analytics import system_analysis
from database.profiling import profiling_Time
from database.maintenance import delete_OldData
from ai.ai_analytics import predict_live,diagnose_system,ai_summary
from ai.process_info import system_snapshot
from ai.LLM_reasoning import analyze_incident 
from api.anomaly import get_model
from database.history import getHistory
import time
import threading

ai_investigation_running = {}
ai_lock = threading.Lock()
ai_latest_result={}

latest_metric = {}
latest_anomaly = {}
latest_summary = {}
latest_issues_by_machine = {}
connection_time = {}

# Creating  a blueprint Instance
metrics_bp = Blueprint('metrics_bp', __name__, url_prefix='/api/metrics')

@metrics_bp.route("/telemetry",methods=["POST"]) 
def receive_telemetry():
    start=time.time()
    global ai_investigation_running
    global ai_latest_result
    global latest_metric
    global latest_anomaly
    global latest_summary
    global latest_issues_by_machine
    global connection_time
    try:
        print("1. Capturing telemetry")
        metric_payload=request.get_json()
        if not metric_payload:
            return jsonify({
                "success":False,
                "error":"No Telemetry data received"
                }),400
        machine_id=metric_payload.get("machine_id")
        # To get each indivial Telmentry 
        if not machine_id:
            return jsonify({
                "success":False,
                "error":"Machine_Id not received !"
                }),400
        print("Machine ID created successfully !")
        connection_time[machine_id]=time.time()
        print("2. Telemetry captured")
        serialized_meterics=TelemetrySeralize.convert_data(metric_payload)
        serialized_meterics["machine_id"]=machine_id
        print("3. Metrics serialized")
        live_vector=[
            serialized_meterics['cpu']['cpu_usage'],
            serialized_meterics['ram']['percent'],
            serialized_meterics['disk']['disk_usage'],
            serialized_meterics['network_activity']['network_sent'],
            serialized_meterics['network_activity']['network_received']
        ]
        anomaly=predict_live(get_model(),live_vector)
        print("4. Anomaly:", anomaly)
        issues=diagnose_system(serialized_meterics)
        print("5. Issues diagnosed")
        summary=ai_summary(anomaly,issues)
        print("6. Summary created")
        save_metric(serialized_meterics,anomaly)
        print("7. Metric saved")
        latest_metric[machine_id] = serialized_meterics
        latest_anomaly[machine_id]= anomaly
        latest_summary[machine_id] = summary
        latest_issues_by_machine[machine_id] = issues
        if anomaly == -1:
            print("8. ANOMALY DETECTED → Getting processes")
            with ai_lock:
                if not ai_investigation_running.get(machine_id,False):
                    ai_investigation_running[machine_id] = True
                    ai_latest_result [machine_id]= None
                    print("9. Starting background AI investigation")
                    thread=threading.Thread(target=run_ai,args=(machine_id,serialized_meterics,anomaly,issues),name=f"AI-Investigation-{machine_id}")
                    thread.start()
                else:
                    print("9. AI investigation already running")
        else:
            print("8. System normal")
        return jsonify({
            "success":True,
            "time_taken":round((time.time()-start)*1000,2),
            "metric":serialized_meterics,
            "anomaly":anomaly,
            "summary":summary,
            "issues":issues,
            "database":"Done"
            }), 200
    except Exception as e:
            return jsonify({
                        "success":False,
                        "error":str(e)
                        }), 500

def run_ai(machine_id,meteric,anomaly,issues):
    global ai_investigation_running
    global ai_latest_result
    try:
        print("Background Ai starting")
        process=meteric["processes"]
        incident=system_snapshot(meteric,anomaly,issues,process)
        ai_analysis=analyze_incident(incident)
        with ai_lock:
            ai_latest_result[machine_id]=ai_analysis
        print("Background AI Result stored")
    except Exception as e:
        print("BACKGROUND AI ERROR:", e)
    finally:
        with ai_lock:
            ai_investigation_running[machine_id] = False
        print(f"BACKGROUND AI investigation finished for {machine_id}")

@metrics_bp.route("/ai",methods=["GET"])
def get_ai():
    machine_id=request.args.get("machine_id")
    if not machine_id:
        return jsonify({
            "success":True,
            "message":"Machine ID is missing"
        }),400
    with ai_lock:
        if ai_investigation_running.get(machine_id,False):
            return jsonify({
                "ai": {
                    "summary":
                        "Anomaly detected. AI investigation is running....",
                    "root_cause":
                        "Investigation in progress.",
                    "contributors": [],
                    "recommendations": [],
                    "confidence": 0.0
                },
                "status":"running",
                "success":True
            }),200
        if machine_id in ai_latest_result:
            result=ai_latest_result[machine_id]
            if result is not None:
                return jsonify({
                    "status":"complete",
                    "success":True,
                    "ai":result
                }),200
        
        return jsonify({
                "ai": {
                    "summary":
                        "System is healthy. No anomaly detected.",
                    "root_cause":
                        "No investigation required.",
                    "contributors": [],
                    "recommendations": [],
                    "confidence": 1.0
                },
                "success":True,
                "status":"healthy"
        }),200

@metrics_bp.route("/live",methods=["GET"])
def get_metrics():
    start=time.time()
    try:
        machine_id = request.args.get("machine_id")
        if not machine_id :
            return jsonify({
                "success":False,
                "connection":False,
                "message":"Machine ID is missing"
            }),404
        if machine_id not in latest_metric:
            return jsonify({
                "success":False,
                "connection":False,
                "message":"No Telemetry received from this machine."
            }),404
        if time.time()-connection_time[machine_id] > 20:
            return jsonify({
                "success":False,
                "connection":False,
                "message":"No recent activities."
            }),404
        
        return jsonify({
            "success":True,
            "time_taken":round((time.time()-start)*1000,2),
            "metric":latest_metric[machine_id],
            "anomaly":latest_anomaly[machine_id],
            "summary":latest_summary[machine_id],
            "issues":latest_issues_by_machine[machine_id],
            "connection":True,
            "database":"Done"
            }), 200

    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e)
                    }), 500

@metrics_bp.route("/summary",methods=["GET"])
def meterics_summary():
    try:
        machine_id = request.args.get("machine_id")
        if not machine_id:
            return jsonify({
                "success": False,
                "error": "Machine ID is missing"
            }), 400
        systemData=system_analysis(machine_id)
        return jsonify({
            "success":True,
            "summary":systemData
        })
    except Exception as e:
        return jsonify({
                "success":False,
                "error":str(e),
                "analysis":"Something went wrong!"
                }), 500

@metrics_bp.route("/history",methods=["GET"])
def meterics_history():
    try:
        machine_id = request.args.get("machine_id")
        if not machine_id:
            return jsonify({
                "success": False,
                "error": "Machine ID is missing"
            }), 400
        start=time.time()
        start_time=float(request.args.get("start"))
        end_time=float(request.args.get("end"))
        page=int(request.args.get("page",1))
        limit=int(request.args.get("limit",20))
        offset=(page-1)*limit
        data=getHistory(machine_id,start_time,end_time,limit,offset)
        duration=time.time()-start
        return jsonify({
            "success":True,
            "history":data,
            "page":page,
            "limit":limit,
            "count":len(data),
            "duration":duration
        }),200
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    "analysis":"hey i am wrong!"
                    }), 500
    
@metrics_bp.route("/profile",methods=["GET"])
def get_profiling_time():
    try:
        result=profiling_Time()
        return jsonify({
            "success":True,
            "results":result
        })
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    "analysis":"Something went wrong!"
                    }),500

@metrics_bp.route("/cleanup",methods=["GET"])
def delete_Rows():
    try:
        result=delete_OldData()
        return jsonify({
            "success":True,
            "results":result
        }),200
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    }),500



