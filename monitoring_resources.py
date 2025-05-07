import psutil
import time
from datetime import datetime
import os
import logging

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
threshold = 80

log_dir = "logs"
os.makedirs(log_dir , exist_ok=True)
log_filename = os.path.join(log_dir,f"report_{timestamp}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_alert(subject , message):
    logging.warning(f"{subject} - {message}")
    print(f"\nSubject : {subject}\nMessage : {message}")

def check_disk():
    usage = psutil.disk_usage("C:\\")
    percent = usage.percent
    if percent > threshold:
        send_alert(subject="ALERT",message=f"Usage disk is at {percent}")
    return percent  # Sempre restituisce percentuale, anche se < 80%

def check_cpu():
    return psutil.cpu_percent(interval=1)

def check_ram():
    return psutil.virtual_memory().percent

def check_network_bandwidth(interval=5):
    # Misura i bytes all'inizio
    net1 = psutil.net_io_counters()
    sent1 = net1.bytes_sent
    recv1 = net1.bytes_recv
   
    # Intervallo di tempo
    time.sleep(interval)

    # Misura i bytes dopo l'intervallo
    net2 = psutil.net_io_counters()
    sent2 = net2.bytes_sent
    recv2 = net2.bytes_recv

    # Calcola velocità di upload e download in bytes per second
    upload_speed = (sent2 - sent1)/interval
    download_speed = (recv2 - recv1)/interval

    # Ritorna i valori
    return upload_speed , download_speed


def save_report():
      try:
        cpu = check_cpu()
        ram = check_ram()
        disk_usage = check_disk()
        upload_speed , download_speed = check_network_bandwidth()

        logging.info(f"CPU usage: {cpu}%")
        logging.info(f"RAM usage: {ram}%")
        logging.info(f"Disk usage: {disk_usage}%")
        logging.info(f"Upload speed : {upload_speed} bytes per seond")
        logging.info(f"Download speed : {download_speed} bytes per second")

      except Exception as e:
          logging.error(f"Errore nella generazione del report: {e}")
          send_alert("Script error", str(e))

if __name__== "__main__":
    save_report()
