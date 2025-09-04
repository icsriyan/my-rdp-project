import psutil
import subprocess
import time
import datetime
import requests

threshold_percentage = 50
included_processes = ['msedge.exe']  # List of process names to include
log_file = "log.txt"
start_time = time.time()
send_log_after_minutes = 60
telegram_bot_token = '7036285968:AAHVNjiq_TDE3BUQPQNiZF47EqIazN4pClw'
chat_id = '1138482440'

def log_cpu_usage():
    with open(log_file, "a") as f:
        for process in psutil.process_iter(['name', 'cpu_percent']):
            process_name = process.info['name']
            cpu_percent = process.info['cpu_percent']
            if cpu_percent > threshold_percentage and process_name not in ['System Idle Process', 'python.exe']:
                f.write(f"{process_name} : {cpu_percent}%\n")
        # Log once after checking all processes

def send_log():
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
    files = {'document': open(log_file, 'rb')}
    data = {'chat_id': chat_id}
    response = requests.post(url, files=files, data=data)

def main():
    start_time = time.time()  # Reset start time at the beginning of each loop iteration
    while True:
        processes_exceeded_threshold = False  # Flag to track if any process exceeds the threshold
        for process in psutil.process_iter(['name', 'cpu_percent']):
            process_name = process.info['name']
            cpu_percent = process.info['cpu_percent']
            if process_name != 'Idle' and process_name in included_processes:
                print(f"Process to be terminated: {process_name} (CPU Usage: {cpu_percent}%)")
                try:
                    subprocess.run(['taskkill', '/F', '/IM', process_name], check=True)
                    print(f"Terminated process: {process_name}")
                    
                except subprocess.CalledProcessError:
                    print(f"Failed to terminate process: {process_name}")
            
            if cpu_percent > threshold_percentage:
                processes_exceeded_threshold = True
        
        if processes_exceeded_threshold:
            log_cpu_usage()

        current_time = time.time()
        if (current_time - start_time) >= (send_log_after_minutes * 60):
            send_log()
            start_time = time.time() + 5 * 60 * 60  # Reset start time to current time plus six hours

        time.sleep(10)  # Adjust the sleep duration as needed

if __name__ == "__main__":
    main()
