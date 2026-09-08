from database.database import get_connection
import sqlite3 as sq

def getHistory(machine_id,start_time,end_time,limit,offsets):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        SELECT id,timeStamp,cpu_usage,ram_usage,disk_usage,network_sent,network_received FROM telemetry
        where machine_id=?
        AND timeStamp BETWEEN ? AND ?
        ORDER BY timeStamp DESC
        LIMIT ? OFFSET ?
    """,(machine_id,start_time,end_time,limit,offsets))
    rows=cursor.fetchall()
    result=[]
    for row in rows:
        result.append ({
            "id":row[0],
            "timeStamp":row[1],
            "cpu_usage":row[2],
            "ram_usage":row[3],
            "disk_usage":row[4],
            "network_sent":row[5],
            "network_received":row[6]
        })
    cursor.close()
    conn.close()
    return result

def get_training_data():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
            SELECT timeStamp,cpu_usage,ram_usage,disk_usage,network_sent,network_received FROM telemetry
        """)
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result

