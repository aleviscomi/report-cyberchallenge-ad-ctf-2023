import subprocess, time, os, datetime

ip2send = "localhost"         # ip della macchina a cui inviare le catture
port2send = "9999"

filters = [{"port": 80, "name": "CTFe-Master"},
            {"port": 5005, "name": "CTFe-1"},
            {"port": 5006, "name": "CTFe-2"},
            {"port": 1234, "name": "NotABook"}]

filenames = [f"capture_{filter['name']}.pcap" for filter in filters]
now = datetime.datetime.now()
folder_name = f"pcaps_{now.hour}{now.minute}{now.second}"
zip_name = folder_name + ".zip"

########################################################################################################################

seconds = int(input("Inserisci la durata (IN SECONDI) della cattura: ")) # secondi di cattura
processes = []

os.system(f"mkdir {folder_name}")
# faccio partire le catture
for i in range(len(filters)):
    cmd = "sudo tcpdump -s0 -w {folder_name}/{filename} port {port}".format(folder_name=folder_name, filename=filenames[i], port=filters[i]['port'])
    print(cmd)
    processes.append(subprocess.Popen(cmd, shell=True))


time.sleep(seconds)

# termino le catture
for i in range(len(processes)):
    processes[i].terminate()

# zippo le catture e le invio al client in ascolto con nc
os.system(f"zip -r {zip_name} {folder_name} && nc {ip2send} {port2send} < {zip_name}")

# elimino la cartella con le catture e la zip
os.system(f"rm -fr {zip_name} {folder_name}")
