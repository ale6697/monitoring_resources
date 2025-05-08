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
    "disk_partitions" : ["C:\\"],
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
partitions = config["disk_partitions"]    

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
    def __init__(self, threshold, partitions):
        self.threshold = threshold
        self.partitions = partitions

    # Funzione che stampa l'alert nel CMD
    def send_alert(self , subject , message):
        logging.warning(f"{subject} - {message}")
        print(f"\nSubject : {subject}\nMessage : {message}")

    # Funzione che controlla l'utilizzo del disco rigido in tutte le partizioni
    def check_disk_all(self):
        for partition in self.partitions:
            try:
                usage = psutil.disk_usage(partition)
                percent = usage.percent
                if percent > self.threshold:
                    self.send_alert(subject="ALERT",message=f"Disk usage on {partition} is at : {percent}%")
                logging.info(f"Disk usage on {partition} : {percent}%")               
            except Exception as e:
                logging.error(f"Errore nel controllo del disco {partition} : {e}")
                self.send_alert("Disk error" ,f"{partition} : {str(e)}")


    #Funzione che controlla l'utilizzo della CPU   
    def check_cpu(self):
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logging.error(f"Errore nel controllo della CPU : {e}")
            self.send_alert("CPU Error", str(e))
            return -1


    #Funzione che controlla l'utilizzo della RAM     
    def check_ram(self):
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logging.error(f"Errore nel controllo della RAM : {e}")
            self.send_alert("RAM Error", str(e))
            return -1

    #Funzione che controlla la velocità in download e upload        
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
        
    # Funzione che controlla la temperatura della CPU , inserita 
    # come commento perchè non disponibile in windows la libreria
    #  psutil.sensors_temperature()
#    def check_temperature_cpu(self):
#        try:
#            temps = psutil.sensors_temperature()
#            if not temps:
#                return None
#            for name , entries in temps.item():
#                for entry in entries:
#                    if entry.current:
#                        return entry.current
#            return None
#        except Exception as e:
#            self.send_alert(f"Temperature error : ", str(e))
#            return None

    # Funzione che controlla i processi attivi
    def check_top_processes(self, limit=5):
        try:
            processes = sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']),
                               key=lambda p: p.info['cpu_percent'],reverse=True)
            return processes[:limit]
        except Exception as e:
            self.send_alert("Process monitor error : ", str(e))
            return[]

    #Funzione che scrive nel report di log   
    def save_report(self):
        try:
            cpu = self.check_cpu()
            ram = self.check_ram()
            self.check_disk_all()
            upload_speed, download_speed = self.check_bandwidth()
          #  cpu_temp = self.check_temperature_cpu()
            top_processes = self.check_top_processes()
            
            #Log risorse di sistema
            logging.info(f"CPU usage : {cpu}%")
            logging.info(f"RAM usage : {ram}%")
            logging.info(f"Upload speed : {upload_speed:.2f} Mbps")
            logging.info(f"Download speed : {download_speed:.2f} Mbps")
           # if cpu_temp is not None:
            #    logging.info(f"CPU temperature : {cpu_temp:.2f}°C")

            #Log processi 
            logging.info("Top processes : ")
            for proc in top_processes:
                logging.info(f"PID : {proc.pid}, Name : {proc.info['name']}, "
                             f"CPU: {proc.info['cpu_percent']}%, MEM: {proc.info['memory_percent']:.2f}%")

            print(f"Report salvato : {log_filename}")

        except Exception as e:
            logging.error(f"Errore nella generazione del report : {e}")
            self.send_alert("Script error" , str(e))


# Inizializza il monitor
monitor = systemMonitor(threshold , partitions)

#Pianificazione periodica
schedule.every(interval).seconds.do(monitor.save_report)

#Main
if __name__ == "__main__":
    print("Inzio monitoraggio...")
    while True:
        schedule.run_pending()
        time.sleep(1)