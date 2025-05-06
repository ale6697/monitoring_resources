import psutil
from datetime import datetime

def send_alert(subject , message):
    print(f"ALERT\nSubject : {subject}\nMessage : {message}")

def check_disk():
    usage = psutil.disk_usage("/")
    percent = usage.percent
    if percent > 80:
        print("Disk usage over 80%")
        send_alert(subject="ALERT DISK USAGE",message=f"Usage disk is at {percent}")
    return percent  # Sempre restituisce percentuale, anche se < 80%

def save_report():
    with open("report.txt", "w") as f:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk_usage = check_disk()
        timestamp =  datetime.now().isoformat()
        f.write(f"CPU usage: {cpu}%\n")
        f.write(f"RAM usage: {ram}%\n")
        f.write(f"Disk usage: {disk_usage}%\n")
        f.write(f"timestamp : {timestamp}")
        f.write("AGGIUNTO LOG DI TEST")


# Chiamata della funzione per generare il report
save_report()
