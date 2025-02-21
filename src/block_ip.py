import subprocess

def block_ip(ip: str):
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        print(f"✅ Zablokowano IP: {ip}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas blokowania IP {ip}: {e}")

if __name__ == "__main__":
    ip_to_block = input("Podaj IP do zablokowania: ")
    block_ip(ip_to_block)

