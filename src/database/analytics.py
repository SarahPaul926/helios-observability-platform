from database.database import get_connection
def system_analysis(machine_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(""" 
               SELECT AVG(cpu_usage),
               MAX(ram_usage) from telemetry
               WHERE machine_id=?
    """,(machine_id,))
    result=cursor.fetchone()
    avg_cpu,max_ram=  result[0],result[1]
    cursor.close()
    conn.close()
    return {"average_cpu":avg_cpu,"maximum_ram":max_ram}


    

