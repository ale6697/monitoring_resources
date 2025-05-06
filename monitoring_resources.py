import psutil
from datetime import datetime
import os
import logging

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_dir = "logs"
os.makedirs(log_dir , exist_ok=True)
log_filename = os.path.join(log_dir,f"report_{timestamp}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_alert(subject , message):
    logging.warning(f"ALERT: {subject} - {message}")
    print(f"ALERT\nSubject : {subject}\nMessage : {message}")

def check_disk():
    usage = psutil.disk_usage("C:\\")
    percent = usage.percent
    if percent > 80:
        send_alert(subject="ALERT DISK USAGE",message=f"Usage disk is at {percent}")
    return percent  # Sempre restituisce percentuale, anche se < 80%

def check_cpu():
    return psutil.cpu_percent(interval=1)

def check_ram():
    return psutil.virtual_memory().percent


def save_report():
      try:
        cpu = check_cpu()
        ram = check_ram()
        disk_usage = check_disk()
        

        logging.info(f"CPU usage: {cpu}%")
        logging.info(f"RAM usage: {ram}%")
        logging.info(f"Disk usage: {disk_usage}%")
        
      except Exception as e:
          logging.error(f"Errore nella generazione del report: {e}")
          send_alert("Script error", str(e))

if __name__== "__main__":
    save_report()
