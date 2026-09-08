import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime


def evaluate_z_score(current_value,history_data,threshold=3):
    mean_Value=np.mean(history_data)
    sigma=np.std(history_data)
    if sigma==0: return 0.0
    z_score=(current_value-mean_Value)/sigma
    if abs(z_score) > threshold: result="ANOMALY"
    else: result="NORMAL"
    return z_score,result

def moving_baselines(data,window=3):
    if window > len(data): raise ValueError("window size can not be greater than the size of data")
    if window <= 0: raise ValueError("window size can not be lesser than or equal to 0")
    baseline=[]
    for i in range(len(data)-window+1):
        baseline.append(np.mean(data[i:window+i]))
    return baseline

def load_dataframe(raw_data):
    column=["timeStamp","cpu_usage","ram_usage","disk_usage","network_sent","network_received"]
    dataframe=pd.DataFrame(raw_data,columns=column)
    return dataframe

def excute_isolationForest(dataframe):
    model =  IsolationForest(contamination=0.10,random_state=45)
    model.fit(dataframe[["cpu_usage","ram_usage","disk_usage","network_sent","network_received"]])## train the model 
    return model

def predict_live(model,live_vector):
    columns=["cpu_usage","ram_usage","disk_usage","network_sent","network_received"]
    live_data=pd.DataFrame([live_vector],columns=columns)
    prediction=model.predict(live_data)
    return -1 if prediction[0]==-1 else 0

def baseline_model():
    model =  IsolationForest(contamination=0.10,random_state=45)
    columns=["cpu_usage","ram_usage","disk_usage","network_sent","network_received"]
    baseline_vector=[[0, 0, 0, 0, 0],
        [10, 10, 10, 10, 10],
        [20, 20, 20, 20, 20],
        [30, 30, 30, 30, 30],
        [40, 40, 40, 40, 40]]
    baseline_data=pd.DataFrame(baseline_vector,columns=columns)
    model.fit(baseline_data)
    return model

def train_Model(rawData):
    df=load_dataframe(rawData)
    if df.empty:
         print("No model for Isolation Forest to train on")
         return baseline_model()
    model=excute_isolationForest(df)
    return model

def diagnose_system(meteric):
    issues=[]
    cpu=meteric["cpu"]["cpu_usage"]
    ram=meteric["ram"]["percent"]
    disk=meteric["disk"]["disk_usage"]
    network_sent=meteric["network_activity"]["network_sent"]
    network_received=meteric["network_activity"]["network_received"]
    if cpu>80:
        issues.append({
            "resource":"CPU",
            "message":f"CPU usage is critically high: {cpu}%"
        })
         
    if ram>80:
            issues.append({
                "resource":"RAM",
                "message":f"RAM usage is critically high: {ram}%"
            })
    if disk>80:
            issues.append({
                "resource":"DISK",
                "message":f"DISK usage is critically high: {disk}%"
            })

    if network_sent>100 or network_received >100 :
                issues.append({
                    "resource":"Network Sent & Network Received",
                    "message":f"Network activity is high:{network_sent} MB sent{network_received} MB received."
                })

    return issues

def ai_summary(anomaly,issues):
    if not issues and anomaly==0:
         return{
               "status":"Normal",
               "summary":"The System is currently operating normally. No sigificant anomalies were detected"
            }
    if issues and anomaly==0:
        resources=[]
        for issue in issues:
                 resources.append(issue["resource"])
        resources_text=",".join(resources)
        summary=(f"High Resource usage has been detected in: {resources_text}.")
        summary+=" ".join(issue["message"] for issue in issues)
        summary+=(
            " The system behaviour is not necessarily statistically anomalous, but the affected resource usage should be investigated.")
        return{
                "status":"Warning",
                "summary":summary
            }
    if not issues and anomaly==-1:
         return {
            "status": "Anomaly",
            "summary": (
                "Unusual system behaviour was detected, "
                "but no specific resource issue was identified."
            )
        }
    if issues and anomaly==-1:
        resources=[]
        for issue in issues:
                    resources.append(issue["resource"])
        resources_text=",".join(resources)
        summary=(f"An anomaly has been detected in the system." f"The affected resource(s) are: {resources_text}.")
        summary+=" ".join(issue["message"] for issue in issues)
        summary += (
            " You may want to check running processes and applications that could be consuming excessive system resources."
        )
        return {
                "status":"CRITICAL",
                "summary":summary
        }
    

    
    

if __name__ == "__main__":
    print("\n==============================")
    print(" HELIOS DIAGNOSTIC TEST")
    print("==============================")

    # --------------------------------
    # Test 1: Completely normal system
    # --------------------------------

    normal_metric = {
        "cpu": {
            "cpu_usage": 40
        },
        "ram": {
            "percent": 50
        },
        "disk": {
            "disk_usage": 60
        },
        "network_activity": {
            "network_sent": 20,
            "network_received": 30
        }
    }

    issues = diagnose_system(normal_metric)

    result = ai_summary(
        anomaly=0,
        issues=issues
    )

    print("\nTEST 1: NORMAL SYSTEM")
    print("Issues:", issues)
    print("Result:", result)


    # --------------------------------
    # Test 2: High CPU and RAM
    # ML says normal
    # --------------------------------

    high_resource_metric = {
        "cpu": {
            "cpu_usage": 93.5
        },
        "ram": {
            "percent": 92.3
        },
        "disk": {
            "disk_usage": 60
        },
        "network_activity": {
            "network_sent": 20,
            "network_received": 30
        }
    }

    issues = diagnose_system(high_resource_metric)

    result = ai_summary(
        anomaly=0,
        issues=issues
    )

    print("\nTEST 2: HIGH CPU + RAM")
    print("Issues:", issues)
    print("Result:", result)


    # --------------------------------
    # Test 3: ML anomaly only
    # --------------------------------

    issues = []

    result = ai_summary(
        anomaly=1,
        issues=issues
    )

    print("\nTEST 3: ML ANOMALY ONLY")
    print("Issues:", issues)
    print("Result:", result)


    # --------------------------------
    # Test 4: Both ML + diagnostics
    # --------------------------------

    issues = diagnose_system(high_resource_metric)

    result = ai_summary(
        anomaly=1,
        issues=issues
    )

    print("\nTEST 4: CRITICAL")
    print("Issues:", issues)
    print("Result:", result)


    # --------------------------------
    # Test 5: High network activity
    # --------------------------------

    network_metric = {
        "cpu": {
            "cpu_usage": 40
        },
        "ram": {
            "percent": 50
        },
        "disk": {
            "disk_usage": 60
        },
        "network_activity": {
            "network_sent": 150,
            "network_received": 500
        }
    }

    issues = diagnose_system(network_metric)

    result = ai_summary(
        anomaly=0,
        issues=issues
    )

    print("\nTEST 5: HIGH NETWORK ACTIVITY")
    print("Issues:", issues)
    print("Result:", result)


    print("\n==============================")
    print(" TESTING COMPLETE")
    print("==============================")
