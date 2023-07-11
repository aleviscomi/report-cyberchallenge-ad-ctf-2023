# Utils

In questa cartella risiedono gli script di utilità sviluppati durante il percorso di addestramento alla finale e utilizzati durante quest'ultima. Di seguito una spiegazione dettagliata di quanto sviluppato.

## Exploit

In questa cartella sono presenti due script utili per il processo di sfruttamento delle vulnerabilità.

### exploit.py

Questo script è stato sviluppato per permettere a tutti i componenti della squadra di scrivere agevolmente e velocemente un exploit una volta individuata una vulnerabilità per un servizio.

Inizialmente, si prevede di impostare alcune costanti che serviranno in seguito:
```python
TEAM_TOKEN = ""			# TOKEN DEL TEAM INVIATO PER EMAIL
CHALLENGE_NAME = ""		# NOME DELLA CHALLENGE PER COME INDICATO IN flagIds
CHALLENGE_PORT = ""		# PORTA DELLA CHALLENGE CONSIDERATA

MY_TEAM = ""			# IP DEL MIO TEAM
NOP_TEAM = "10.60.0.1"	# IP DEL NOP TEAM
```

Successivamente sono presenti alcune funzioni di utilità che potrebbero essere vantaggiose durante la scrittura dell'exploit. Nello specifico abbiamo:
* _generate\_random\_string(length)_, che costruisce e restituisce una stringa casuale di lunghezza _length_. Questa può essere utile in casi come la registrazione di un utente, per generare il suo username. In queste situazioni, infatti, non sarà possibile registrare più di un utente con lo stesso username e, poiché ci ritroveremmo a registrare (almeno) ad ogni tick un utente nuovo sulle stesse macchine, non possiamo registrare utenti con username fissati.
```python
def generate_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
```

* _generate\_fake\_flag()_, che permette di generare e restituire una stringa che segue la regex delle flag. Questa funzione può essere utile nel caso in cui si vuole confondere il team attaccato durante l'exploit.
```python
def generate_fake_flag():
    letters = string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(letters) for i in range(31)) + "="
    return result_str
```

* _add\_noise(url, header=None, payload=None, session=None)_, che permette di effettuare delle richieste verso determinati URL. Questa, come la precedente, può essere utile anche per creare del "rumore" e confondere l'avversario durante l'exploit.
```python
def add_noise(url, header=None, payload=None, session=None):
	if payload == None:
		if session == None:
			if header == None:
				requests.get(url, timeout=3)
			else:
				requests.get(url, headers=header, timeout=3)
		else:
			if header == None:
				session.get(url, timeout=3)
			else:
				session.get(url, headers=header, timeout=3)
	else:
		if session == None:
			if header == None:
				requests.post(url, data=payload, timeout=3)
			else:
				requests.post(url, headers=header, data=payload, timeout=3)
		else:
			if header == None:
				session.post(url, data=payload, timeout=3)
			else:
				session.post(url, headers=header, data=payload, timeout=3)

	print(f"Rumore aggiunto - {url} : {payload}")
```
Oltre alle funzioni di utilità discusse è presente anche una struttura dati che può essere utile durante la scrittura di un exploit. Infatti, non sempre le challenge hanno bisogno dei flagIds per essere risolte. In questi casi, è stata creata la struttura denominata **noFlagIds**. Essa non è altro che un oggetto JSON che ricalca la struttura classica dei flagIds, avendo però dei flagIds impostati a stringa vuota. Questa è stata inserita per far sì che la struttura di tutto lo script rimanga la medesima anche nel caso in cui non ci siano hint da parte del gameserver.
```python
noFlagIds = {CHALLENGE_NAME: {'10.60.0.1': [''], '10.60.1.1': [''], '10.60.2.1': [''], '10.60.3.1': [''], '10.60.4.1': [''], '10.60.5.1': [''], '10.60.6.1': [''], '10.60.7.1': [''], '10.60.8.1': [''], '10.60.9.1': [''], '10.60.10.1': [''], '10.60.11.1': [''], '10.60.12.1': [''], '10.60.13.1': [''], '10.60.14.1': [''], '10.60.15.1': [''], '10.60.16.1': [''], '10.60.17.1': [''], '10.60.18.1': [''], '10.60.19.1': [''], '10.60.20.1': [''], '10.60.21.1': [''], '10.60.22.1': [''], '10.60.23.1': [''], '10.60.24.1': [''], '10.60.25.1': [''], '10.60.26.1': [''], '10.60.27.1': [''], '10.60.28.1': [''], '10.60.29.1': [''], '10.60.30.1': [''], '10.60.31.1': [''], '10.60.32.1': [''], '10.60.33.1': [''], '10.60.34.1': [''], '10.60.35.1': [''], '10.60.36.1': [''], '10.60.37.1': [''], '10.60.38.1': [''], '10.60.39.1': [''], '10.60.40.1': [''], '10.60.41.1': [''], '10.60.42.1': [''], '10.60.43.1': ['']}}
```

A questo punto andiamo ad analizzare lo script seguendo l'ipotetico flusso di esecuzione. Ovviamente è stata inserita una funzione _main()_, punto di ingresso dello script.
```python
def main():
	test()
	# attack()
	# attack_with_threads()
```

Come vediamo, sono presenti le chiamate a 3 funzioni, ma solo 1 è decommentata. Questo perché solo una di queste 3 dovrà essere eseguita e, inizialmente, per testare quanto si sta scrivendo sarà utile che venga eseguita la funzione _test()_.

La funzione _test()_ prevede di impostare l'ip della macchina sulla quale si vuole provare lo script (per ovvie ragioni si consiglia il NOP TEAM) e un eventuale hint (flagId) fornito dal gameserver. Fatto ciò, _test()_ va ad eseguire la funzione ***get_flag(ip, CHALLENGE_PORT, hint)***, cuore dell'intero script in cui si dovrà scrivere l'exploit vero e proprio. Se esso funzionerà, la funzione restituirà una flag che verrà inserita nella variabile _flag_ e stampata. Sono, inoltre, commentate alcune righe che permetterebbero di creare una lista con la flag prelevata e di sottometterla, così da provare ad effettuare il first blood più velocemente. All'occorrenza queste possono, quindi, essere decommentate e utilizzate.

```python
def test():
	ip = ""
	hint = ""

	try:
		flag = get_flag(ip, CHALLENGE_PORT, hint)
	except Exception as e:
		print(f"ERR: {e}")
		return
	
	print(flag)
	
	# flags = [flag]
	# print("\nPutting flags...")
	# r = requests.put('http://10.10.0.1:8080/flags', headers={'X-Team-Token': TEAM_TOKEN}, json=flags).text
	# print(r)
```

Come dicevamo, _get\_flag_ è il cuore dell'intero script. Questo sarà, infatti, il punto in cui inserire il proprio exploit. L'exploit dovrà essere scritto in modo tale che, preso un ip e una porta e un eventuale hint (flagId), si vada a recuperare la flag associata a quel flagId, restituendola.

```python
def get_flag(ip, port, hint):
	# PASSAGGI NECESSARI A PRELEVARE UNA FLAG

	flag = ""

	# RESTITUISCI LA FLAG
	return flag
```

Una volta che l'exploit è stato testato tramite la funzione _test()_, l'idea è di andare a commentare questa chiamata a funzione nel main, per decommentare la chiamata a _attack()_.

La funzione _attack()_ si occupa, inizialmente, di andare a recuperare i flagIds della challenge specificata in _CHALLENGE\_NAME_. Questi vengono poi passati alla funzione _exploit_, che si occuperà di scorrerli e di richiamare _get\_flag_. La funzione _exploit_ restituirà la lista delle flag rubate da tutte le altre macchine. Queste saranno quindi sottomesse al gameserver, si farà una sleep per attendere il prossimo tick e si rieseguirà l'attacco.

*NOTA: nel caso in cui non dovessero essere presenti flagIds per la challenge in questione, basta commentare la riga che fa la richiesta al gameserver e decommentare la riga che imposta la struttura noFlagIds*

```python
def attack():
	while True:
		print("Running exploit...")

		flagids = requests.get("http://10.10.0.1:8081/flagIds?service={CHALLENGE_NAME}").json()
		# flagids = noFlagIds

		flags = exploit(flagids)
		
		print()
		print(flags)

		now = datetime.datetime.now()
		print(f"\nPutting flags (ORA: {now.hour}:{now.minute}:{now.second})...")
		r = requests.put('http://10.10.0.1:8080/flags', headers={'X-Team-Token': TEAM_TOKEN}, json=flags).text
		print(r)

		print("Exploit ok...\n\nRepeat after sleep...")
		print("\n")

		time.sleep(120)
```

Come summenzionato, la funzione _exploit(flagids)_ si occupa di scorrere tutti gli IP (scartando il NOP TEAM e il proprio TEAM). Per ogni ip si scorrono poi i flagIds. Dunque, per ogni flagId di ogni IP, si richiama la funzione _get\_flag_ che restituirà la flag associata. Questa verrà poi inserita nella lista che comprenderà tutte le flag rubate.

```python
def exploit(flagids):
	flag_list = []
	c = 1
	size = len(flagids[CHALLENGE_NAME])
	for ip in flagids[CHALLENGE_NAME]:
		print(f"{ip}\t-\t{c} / {size} ...")

		if ip == NOP_TEAM or ip == MY_TEAM:
			c += 1
			continue

		for hint in flagids[CHALLENGE_NAME][ip]:
			try:
				flag = get_flag(ip, CHALLENGE_PORT, hint)
				print(flag)
			except Exception as e:
				print("ERR: {}".format(e))
				continue
			if flag not in flag_list:
				flag_list.append(flag)

		c += 1
	return flag_list
```

Infine, ricordiamo che nel main era possibile effettuare anche la chiamata alla funzione *attack_with_threads()*. Questa funzione è stata prevista nel caso in cui l'exploit, per varie ragioni, dovesse essere troppo lento. A differenza di _attack()_, infatti, questa funzione va a richiamare la funzione *exploit_with_threads(flagids)*.

```python
def attack_with_threads():
	global flags
	global threads
	while True:
		flags = []
		threads = []
		print("Running exploit...")

		flagids = requests.get("http://10.10.0.1:8081/flagIds?service={CHALLENGE_NAME}").json()
		# flagids = noFlagIds

		exploit_with_threads(flagids)
		
		print()
		print(flags)

		now = datetime.datetime.now()
		print(f"\nPutting flags (ORA: {now.hour}:{now.minute}:{now.second})...")
		r = requests.put('http://10.10.0.1:8080/flags', headers={'X-Team-Token': TEAM_TOKEN}, json=flags).text
		print(r)

		print("Exploit ok...\n\nRepeat after sleep...")
		print("\n")

		time.sleep(120)
```
La funzione *exploit_with_threads(flagids)*, a differenza di _exploit(flagids)_, si occupa di andare ad istanziare un thread per ogni IP. Ogni thread si occuperà poi di andare a recuperare tutte le flag associate a quell'IP scorrendo i vari (ed eventuali) flagIds.

```python
def exploit_with_threads(flagids):
	c = 1
	size = len(flagids[CHALLENGE_NAME])
	for ip in flagids[CHALLENGE_NAME]:
		print(f"{ip}\t-\t{c} / {size} ...")
		
		if ip == NOP_TEAM or ip == MY_TEAM:
			c += 1
			continue

		thread = Attacker(ip, flagids)
		threads.append(thread)
		thread.start()

		c += 1
	
	for thread in threads:
		thread.join()
```

Questa funzione utilizza i threads attraverso l'uso della classe _Attacker_ che eredita appunto da Thread. Per evitare problemi di accesso concorrente alla lista delle flag condivisa tra i vari thread, quando questi vanno ad inserire le proprie flag recuperate, è stato fatto uso anche dei lock.

```python
lock = Lock()

class Attacker(Thread):
	def __init__(self, ip, flagids):
		Thread.__init__(self)
		self.ip = ip
		self.flagids = flagids
		
	def run(self):
		flag_list = []
		for hint in self.flagids[CHALLENGE_NAME][self.ip]:
			try:
				flag = get_flag(self.ip, CHALLENGE_PORT, hint)
				print(flag)
			except Exception as e:
				print("ERR: {}".format(e))
				continue
			if flag not in flag_list:
				flag_list.append(flag)
	
		lock.acquire()
		flags.extend(flag_list)
		lock.release()
```

Ricapitolando, questo script permette di scrivere l'exploit all'interno della funzione *get_flag* testandolo tramite la funzione *test*. Quando l'exploit è pronto e funzionante, basta commentare *test()* dentro il main e decommentare *attack()* se l'exploit è sufficientemente veloce, o *attack_with_threads()* in caso contrario.


### submit_one_flag.py

Questo script è stato sviluppato per fare in modo che quando si trova manualmente una flag, si possa concorrere ad effettuare il first blood sulla challenge in questione, hardcodando la flag nello script e sottomettendo tale flag al gameserver.

```python
TEAM_TOKEN = ""     # TOKEN DEL TEAM INVIATO PER EMAIL

flag = ""       # FLAG RECUPERATA

flags = [flag]
print("Putting flags...")
r = requests.put('http://10.10.0.1:8080/flags', headers={'X-Team-Token': TEAM_TOKEN}, json=flags).text
print(r)
```


## Catture

In questa cartella sono presenti due script utili per il processo di cattura dei pacchetti.

### capture_all.py

Questo script serve ad automatizzare la cattura dei pacchetti tramite tcpdump. In particolare, tramite esso è possibile impostare una durata in secondi e catturare il traffico sulla propria macchina per la durata impostata. Ciò viene fatto per ogni servizio impostato, creando un pcap per ogni servizio. Questi file vengono poi zippati insieme e si fornisce il comando veloce per scaricare tale zip con scp.

Come possiamo vedere, bisogna impostare inizialmente l'ip della propria macchina e una struttura dati che identifica porte e nomi dei servizi che si vogliono catturare. Di seguito un esempio.

```python
ip = "10.60.36.1"     # ip vulnbox

filters = [{"port": 80, "name": "CTFe-Master"},
            {"port": 5005, "name": "CTFe-1"},
            {"port": 5006, "name": "CTFe-2"},
            {"port": 1234, "name": "NotABook"}]
```

In seguito si generano i nomi dei file di cattura e della cartella zip e si richiede la durata in secondi della cattura.

```python
seconds = int(input("Inserisci la durata (IN SECONDI) della cattura: ")) # secondi di cattura
```

A questo punto esegue tcpdump in modo separato, per ogni porta indicata, così da creare un pcap differente per ogni servizio. Ciò è possibile grazie all'uso della libreria _subprocess_ che permette di eseguire i comandi in background.

```python
for i in range(len(filters)):
    cmd = "sudo tcpdump -i game -s0 -w {filename} port {port}".format(filename=filenames[i], port=filters[i]['port'])
    print(cmd)
    processes.append(subprocess.Popen(cmd, shell=True))
```

Fatto ciò, si fa una sleep per quanto impostato da input e si terminano i processi che eseguono tcpdump in background.

```python
time.sleep(seconds)

# termino le catture
for i in range(len(processes)):
    processes[i].terminate()
```

Alla fine di tutto si zippano tutte le catture insieme e si eliminano le singole catture. Viene poi mostrato, per una questione di velocità, il comando scp da eseguire in locale per scaricare la zip.

```python
# zippo tutte le catture
files = ' '.join(file for file in filenames)
cmd = f"zip {zip_name} " + files
os.system(cmd)

for i in range(len(filenames)):
    os.system("rm {filename}".format(filename=filenames[i]))

# scarico la cartella zippata
print(f"Scarica in locale con: scp root@{ip}:/root/catture/{zip_name} .")
```


### capture.py

Questo script, a differenza del precedente, permette all'utente di specificare direttamente da terminale le porte per cui si vuole catturare il traffico e genera un pcap contenente tutto il traffico catturato (non lo divide per servizio). Alla fine si indica come scaricare tale cattura con netcat.

```python
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
```