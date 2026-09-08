import psutil
import time
def get_process(limit=10):
    process=[]
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except(psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    time.sleep(0.1)
    for p in psutil.process_iter():
        try:
            process.append({
                "process_id":p.pid,
                "name":p.name(),
                "cpu_percent":p.cpu_percent(None),
                "memory_percent":p.memory_percent()
            })
        except(psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_cpu = sorted(
        process,
        key=lambda process: process["cpu_percent"],
        reverse=True
    )[:limit]

    top_ram = sorted(
        process,
        key=lambda process: process["memory_percent"],
        reverse=True
    )[:limit]

    combined = {}

    for process in top_cpu:
        combined[process["process_id"]] = process

    for process in top_ram:
        combined[process["process_id"]] = process

    return list(combined.values())

def get_cpu_percent(limit=5):
    process_list=get_process(limit)
    process_list.sort(key=lambda process_list:process_list["cpu_percent"],reverse=True)
    return process_list[:limit]

def get_ram_percent(limit=5):
    process_list=get_process(limit)
    process_list.sort(key=lambda process_list:process_list["memory_percent"],reverse=True)
    return process_list[:limit]

