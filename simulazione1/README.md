# Simulazione 1

Prima simulazione in formato Attack/Defense svolta il 9 e 10 giugno per l'addestramento previsto dal percorso CyberChallengeIT.

I servizi qui proposti erano:
* BioMarkt
* CC_Market
* CrashAir
* MOOZ

## CrashAir
_Categoria: web_

CrashAir è un'applicazione web che permette di prenotare voli a basso prezzo. Essa fornisce un'area riservata in cui ci sono 3 sezioni. La sezione _Reservations_ è quella principale che permette la prenotazione di un volo, con la possibilità di scegliere il proprio posto e di richiedere il check-in online. Inoltre, permette di aggiungere degli _optionals_. Gli optionals possono essere creati e personalizzati attraverso la sezione _Optionals_. Infine, la sezione _Checkout_ è relativa al processo di pagamento e permette di generare un ticket - per le prenotazioni create dall'utente - con le informazioni selezionate.

![alt text](imgs/crashair-login.png)

![alt text](imgs/crashair-cover.png)

### Vulnerabilità 1 - SQLi

La prima vulnerabilità individuata è relativa ad una SQLi nel campo della password:

![alt text](imgs/crashair-sqli.png)

Come è possibile infatti vedere, la password passata come parametro alla funzione get_user viene inserita nella query senza effettuare alcun controllo preliminare.

**Attenzione: potrebbe sembrare che ci sia una vulnerabilità ancora più semplice e che permetta di loggarsi semplicemente non passando il campo della password. Tuttavia, per come gestita nel main la variabile "password" che viene poi passata a get_user, nel caso in cui non si passi questo campo, viene impostata a "" e non a None. È stato infatti provato questo tipo di attacco, ma per il motivo descritto non ha funzionato.**

#### Exploit

Poiché il gameserver forniva gli id degli optionals creati da alcuni utenti (come flagIds), l'idea è stata la seguente.

Per ogni flagId, innanzitutto si registrava un utente casuale per poter accedere all'endpoint "/optionals" e verificare il nome dell'utente relativo al flagId in questione (la flag si trovava sotto il campo "Instructions" relativo al flagId, che però poteva essere visto solo dall'utente che aveva creato l'optional).

![alt text](imgs/crashair-exp1.png)

Successivamente si faceva il login per questo utente eseguendo l'SQL Injection, inserendo nel campo password la stringa _" or 1=1 -- -_.

![alt text](imgs/crashair-exp12.png)

Infine, navigando sulla pagina "/optionals" trovavamo, come indicato prima, sotto la voce "Instructions" la flag ricercata. Questa volta ovviamente era visibile perché a visualizzarla era l'utente che l'aveva creata

![alt text](imgs/crashair-exp13.png)

#### Patch

La patch prevedeva di andare ad evitare di hardcodare l'input dell'utente nella query. Per farlo sono stati usati i prepared statement che già in parte il codice utilizzava.

![alt text](imgs/crashair-patch1.png)


### Vulnerabilità 2 - IDOR in Optionals

La seconda vulnerabilità individuata era una IDOR negli optionals, in quanto era possibile specificare direttamente nell'URL l'id di un optional per accedere alle sue informazioni, tra cui era presente anche la password che era stata impostata per quell'optional.

A cosa serviva la password per un optional? In pratica, l'applicazione permetteva di prenotare un volo inserendo un optional creato da un altro utente. Tuttavia, per poter fare il checkout di una prenotazione che utilizzava un optional di qualcun'altro, era necessario inserire la password di quest'optional, che era possibile recuperare come spiegato. A quel punto, come visto nella sezione precedente, bastava fare il checkout per ricevere il ticket che presentava la flag nel campo "Instructions".

#### Exploit

Per prima cosa si registrava un utente per poter accedere all'endpoint "/optionals". 

![alt text](imgs/crashair-exp2.png)

Successivamente, si sfruttava l'IDOR andando a recuperare la password dell'optional in questione (ricordiamo che l'id degli optional che contenevano le flag erano forniti dal gameserver), accedendo all'endpoint _"/optionals/\<optionalId\>"_

![alt text](imgs/crashair-exp22.png)

Fatto ciò, si prenotava un volo impostando l'optional id summenzionato

![alt text](imgs/crashair-exp23.png)

A questo punto si passava a fare il checkout andando ad inserire la password recuperata in precedenza. Si aspettava la generazione del ticket e si recuperava la flag dal campo "Instructions".

![alt text](imgs/crashair-exp24.png)

#### Patch

Per fixare il problema, di conseguenza, è stato necessario aggiungere un controllo facendo in modo che gli utenti potessero accedere alle info solo dei propri optionals.

Innanzitutto, quindi, è stata modificata la funzione _get\_single\_optional_ (in database.py), prendendo come parametro, oltre a ID, anche username (impostato di default a None per evitare di compromettere porzioni di codice che utilizzavano tale funzione passando solo ID).

![alt text](imgs/crashair-patch2.png)

Questo username si riferisce all'utente correntemente loggato. In questo modo si verifica se il proprietario dell'optional coincide con l'utente loggato. Se così non è, si restituisce None che porterà ad un error 401.

![alt text](imgs/crashair-patch22.png)

Infine, ovviamente, si modifica main.py per passare questo username alla funzione get_single_optional.

![alt text](imgs/crashair-patch23.png)



## MOOZ
_Categoria: crypto_

Mooz è una piattaforma per lo scambio di messaggi. 
Un utente può:
* Registrarsi
* Effettuare il login
* Inviare/Ricevere un messaggio
* Visualizzare i messaggi inviati (anche relativamente ad un solo utente)

### Exploit 

La flag da trovare era nascosta in un messaggio cifrato inviato da un utente A ad un utente B (entrambi ricavabili da flagIds).
La piattaforma, però, permetteva di ricavare il messaggio tramite un identificativo. Il messaggio era cifrato utilizzando DES.
La vulnerabilità consiste nel non aver nascosto a dovere i dati per la generazione delle chiavi degli utenti per cui, risolvendo il problema del logaritmo discreto e compiendo qualche operazione complementare, si è riusciti a calcolare la chiave di sessione e decifrare il messaggio.

![Gatto carino](imgs/Mooz.png)

### Patch

La patch trovata prevedeva di inserire un valore errato molto alto in /get_public. In questo modo, non solo non si esponevano informazioni importanti, ma si potevano anche far bloccare gli script avversari più deboli.


## CCMarket
_Categoria: pwn_

![Gatto carino](imgs/logo.png)

CCMarket è una challenge di pwn. In CCmarket dopo aver fatto l'accesso si ha disposizione una quota di soldi per acquistare oggetti e si può scegliere se accettare gli oggetti sul mercato oppure se creare oggetti da mettere sul mercato. Se acquistiamo gli oggetti forniti nei flagID si ottengono le flag, ovviamente non abbiamo a disposizione abbastanza soldi per acquistare i flagID, dato che il loro prezzo è MAX_INT di C. 




### Vulnerabilità - Si può generare un prezzo negativo
Il problema è che CCMarket da la possibilità di aggiungere sul mercato oggetti che hanno un prezzo negativo. In questo modo, quando acquistiamo questi oggetti, i soldi saranno aggiunti anziché essere sottratti.

Viene illustrato l'exploit.

In questa prima fase si interagisce con il servizio, facendo una registrazione di un utente e facendo il login.

![Gatto carino](imgs/1.png)

Nella seconda fase si aggiunge l'oggetto con prezzo -MAX_INT sul mercato.

![Gatto carino](imgs/2.png)

Nella terza fase compriamo l'oggetto con prezzo negativo

![Gatto carino](imgs/3.png)

Nella quarta ed ultima fase compriamo l'oggetto con dentro la flag e ne analizziamo il contenuto per ottenere la flag.

![Gatto carino](imgs/4.png)




### Patch
Una patch che era possibile implementare era quella di verificare che un oggetto da immettere sul mercato potesse avere solo un prezzo positivo. Modificando questa funzione:

![Gatto carino](imgs/funzione.png)

Andando a modificare la funzione **strncpy** con il metodo del PRELOADING e inserendo all'interno della funzione una verifica sul prezzo. Questo metodo non era però noto al tempo della simulazione quindi non si è riusciti a patchare.



## BioMarkt
_Categoria: web_
