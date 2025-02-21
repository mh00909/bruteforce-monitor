import re
import time
from datetime import datetime
from src.block_ip import block_ip

LOG_PATH = "/var/log/auth.log"
OUTPUT_LOG = "logs/auth_attempts.log"
MAX_ATTEMPTS = 3  # Próg prób logowania

def monitor_login_attempts():
    failed_attempts = {}

    with open(LOG_PATH, "r") as log_file:
        logs = log_file.readlines()

    for line in logs:
        if "Failed password" in line:
            match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)
            if match:
                ip = match.group(1)
                failed_attempts[ip] = failed_attempts.get(ip, 0) + 1

    return failed_attempts

def save_attempts_to_log(ip, attempts):
    with open(OUTPUT_LOG, "a") as log_file:
        log_file.write(f"{datetime.now()} - IP: {ip} - Próby: {attempts}\n")

def main():
    print("🔎 Monitorowanie prób logowania... (Ctrl+C, aby zakończyć)")
    try:
        while True:
            attempts = monitor_login_attempts()
            for ip, count in attempts.items():
                save_attempts_to_log(ip, count)
                if count >= MAX_ATTEMPTS:
                    print(f"🚨 Podejrzane IP: {ip} - Próby: {count}. Blokowanie...")
                    block_ip(ip)
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n❌ Monitorowanie zakończone.")

if __name__ == "__main__":
    main()
