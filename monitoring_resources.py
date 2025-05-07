import psutil
import time
from datetime import datetime
import os
import logging
import json
import schedule  

# Configurazione
config_file = "monitor_config.json"
default_config = {
    "threshold" : 80,
    "log_dir" : "logs",
    "check_interval" : 60,
    "disk_partition" : "C:\\",
    "alert_email" : "ale.derossi97@gmail.com"
}

# Se non esiste il file di configurazione lo creo 
if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        json.dump(default_config, f ,indent=4)
        print(f"File di configurazione creato : {config_file}")


# Carico il file di configurazione
with open(config_file, "r") as f:
    config = json.load(f)

# Setto i dati in base al file di configurazione
threshold = config["threshold"]
log_dir = config["log_dir"]
interval = config["check_interval"]
partition = config["disk_partition"]    

# Creo la directory dei log con nome formattato come report_timestamp
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir,f"report_{timestamp}.log")

# Setto la configurazione dei file di log
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class systemMonitor:
    def __init__(self, threshold, partition):
        self.threshold = threshold
        self.partition = partition

    def send_alert(self , subject , message):
        logging.warning(f"{subject} - {message}")
        print(f"\nSubject : {subject}\nMessage : {message}")
    
    def check_disk(self):
        try:
            usage = psutil.disk_usage(self.partition)
            percent = usage.percent
            if percent > self.threshold:
                self.send_alert(subject="ALERT",message=f"Disk usage is at : {percent}%")
                return percent
        except Exception as e:
            logging.error(f"Errore nel controllo del disco : {e}")
            self.send_alert("Disk error" ,str(e))
            return -1
        
    def check_cpu(self):
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logging.error(f"Errore nel controllo della CPU : {e}")
            self.send_alert("CPU Error", str(e))
            return -1
        
    def check_ram(self):
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logging.error(f"Errore nel controllo della RAM : {e}")
            self.send_alert("RAM Error", str(e))
            return -1
        
    def check_bandwidth(self):
        try:
            net1 = psutil.net_io_counters()
            time.sleep(interval)
            net2 = psutil.net_io_counters()

            upload_speed = (net2.bytes_sent - net1.bytes_sent )/interval
            download_speed = (net2.bytes_recv - net1.bytes_recv )/interval

            upload_speed_Mbps = upload_speed * 8 / 1_000_000
            download_speed_Mbps = download_speed * 8 / 1_000_000

            return upload_speed_Mbps, download_speed_Mbps
        except Exception as e:
            logging.error(f"Errore nel controllo della rete: {e}")
            self.send_alert("Network error", str(e))
            return -1 , -1
        
    def save_report(self):
        try:
            cpu = self.check_cpu()
            ram = self.check_ram()
            disk_usage = self.check_disk()
            upload_speed, download_speed = self.check_bandwidth()

            logging.info(f"CPU usage : {cpu}%")
            logging.info(f"RAM usage : {ram}%")
            logging.info(f"Disk usage : {disk_usage}%")
            logging.info(f"Upload speed : {upload_speed:.2f} Mbps")
            logging.info(f"Download speed : {download_speed:.2f} Mbps")

            print(f"Report salvato : {log_filename}")

        except Exception as e:
            logging.error(f"Errore nella generazione del report : {e}")
            self.send_alert("Script error" , str(e))


# Inizializza il monitor
monitor = systemMonitor(threshold , partition)

#Pianificazione periodica
schedule.every(interval).second.do(monitor.save_report)

if __name__ == "__main__":
    print("Inzio monitoraggio...")
    while True:
        schedule.run_pending()
        time.sleep(1)