import subprocess, time, os, datetime

#############################################################
#                                                           #
#   1. INSTALLARE PRIMA zip SULLA VULNBOX                   #
#                                                           #
#   2. INSERIRE QUESTO SCRIPT NEL PERCORSO /root/capture    #
#                                                           #
#############################################################

ip = "10.60.36.1"                   # ip vulnbox

filters = [{"port": 80, "name": "CTFe-Master"},
            {"port": 5005, "name": "CTFe-1"},
            {"port": 5006, "name": "CTFe-2"},
            {"port": 1234, "name": "NotABook"}]

filenames = [f"capture_{filter['name']}.pcap" for filter in filters]
now = datetime.datetime.now()
zip_name = f"pcaps_{now.hour}{now.minute}{now.second}.zip"

########################################################################################################################

seconds = int(input("Inserisci la durata (IN SECONDI) della cattura: ")) # secondi di cattura
processes = []


# faccio partire le catture
for i in range(len(filters)):
    cmd = "sudo tcpdump -i game -s0 -w {filename} port {port}".format(filename=filenames[i], port=filters[i]['port'])
    print(cmd)
    processes.append(subprocess.Popen(cmd, shell=True))


time.sleep(seconds)

# termino le catture
for i in range(len(processes)):
    processes[i].terminate()

# zippo tutte le catture
files = ' '.join(file for file in filenames)
cmd = f"zip {zip_name} " + files
os.system(cmd)

for i in range(len(filenames)):
    os.system("rm {filename}".format(filename=filenames[i]))

# scarico la cartella zippata
print(f"Scarica in locale con: scp root@{ip}:/root/catture/{zip_name} .")
