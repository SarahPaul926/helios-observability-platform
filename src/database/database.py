import sqlite3 as sq
import time
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "telemetry_history.db"
def get_connection():
    connection = sq.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False
    )
    connection.execute("PRAGMA foreign_keys=ON")
    return connection
def create_Table():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id TEXT,
                    timeStamp REAL,
                    cpu_usage REAL,
                    ram_usage REAL,
                    disk_usage REAL,
                    network_sent INTEGER,
                    network_received INTEGER,
                    anomaly_flag INTEGER 
                )             
    """)
    conn.commit()
    conn.close()


def save_metric(metric,anomaly):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry(machine_id,timeStamp,cpu_usage,ram_usage,disk_usage,network_sent,network_received,anomaly_flag) VALUES (?,?,?,?,?,?,?,?)
    """,(
        metric["machine_id"],
        metric["time"],
        metric['cpu']['cpu_usage'],
        metric['ram']['percent'],
        metric['disk']['disk_usage'],
        metric['network_activity']['network_sent'],
        metric['network_activity']['network_received'],
        anomaly
    ))
    conn.commit()
    conn.close()

def create_index():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_timestamp
        ON telemetry(timeStamp)
    """)
    conn.commit()
    conn.close()

## To 2nd Table for Process Telmentary -- To find the cause
def create_Process_Table():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_telemetry(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timeStamp REAL,
                    process_id INTEGER,
                    name TEXT,
                    cpu_usage REAL,
                    memory_usage REAL
                )             
    """)
    conn.commit()
    conn.close()

def create_process_index():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_process_timestamp
        ON process_telemetry(timeStamp)
    """)
    conn.commit()
    conn.close()

def save_process_metric(process):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO process_telemetry(timeStamp,process_id,name,cpu_usage,memory_usage) VALUES (?,?,?,?,?)
    """,(
        time.time(),
        process["process_id"],
        process["name"],
        process["cpu_percent"],
        process['memory_percent'],
    ))
    conn.commit()
    conn.close()
