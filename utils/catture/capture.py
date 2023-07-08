import subprocess, time, os

ip = "10.60.36.1"                   # ip vulnbox
nc_port = "9999"                    # porta sulla quale aprire netcat per il download della cattura

ports = input("Inserisci le porte da catturare (separate da uno spazio): ").strip().split(" ") # filtri
filters = "or ".join([f'port {x} ' for x in ports]).strip()
print()

chall = input("Inserisci il nome della cattura: ") # nome challenge
filename = f"capture_{chall}.pcap"  # nome file di cattura
print()

seconds = int(input("Inserisci la durata (IN SECONDI) della cattura: ")) # secondi di cattura


cmd = "sudo tcpdump -i game -s0 -w {filename} {filters}".format(filename=filename, filters=filters)
print(cmd)
process = subprocess.Popen(cmd, shell=True)
time.sleep(seconds)
process.terminate()

print("Scarica in locale con: nc -w1 {ip} {nc_port} > {filename}".format(ip=ip, filename=filename, nc_port=nc_port))
os.system("nc -nvlp {nc_port} < {filename}".format(nc_port=nc_port, filename=filename))
os.system("rm {filename}".format(filename=filename))

# su locale lanciare: nc -w1 {ip} 9999 > {filename}
