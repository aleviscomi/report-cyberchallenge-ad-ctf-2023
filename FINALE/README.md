# Gara Nazionale CyberChallengeIT 2023 (CTF A/D)

La gara nazionale di CyberChallengeIT svolta il 29/06/2023 al campus ILO di Torino ha visto la presenza di 4 servizi sviluppati che mettevano a disposizione 7 flag stores differenti (alcuni servizi avevano più di un flag store, al contrario di tutte le edizioni precedenti in cui si aveva un solo flag store per ogni servizio per un totale di soli 4 flag stores).

I servizi - che proponevano challenge relative alle categorie _web_, _crypto_ e _binary_ - erano i seguenti:
* CheesyCheats (2 flag stores);
* Gabibbi Towers (2 flag stores);
* GadgetHorse (2 flag stores);
* MineCClicker (1 flag store).

Dei 7 flag stores presenti, il team è riuscito a costruire 4 exploit funzionanti e a patcharne altrettanti. Nello specifico sono stati exploitati e patchati i seguenti:
* GabibbiTowers-2;
* GadgetHorse-1;
* GadgetHorse-2;
* MineCClicker;

Inoltre, è molto importante notare che solo pochissime squadre sono riuscite ad attaccare i 3 flag stores mancanti.

Come possiamo infatti vedere dall'immagine:

![alt text](imgs/scoreboard_freeze.png)

al momento del freeze della classifica (-2 ore), solo 1 team (su 42) era riuscito ad attaccare CheesyCheats-1 e GabibbiTowers-1, mentre solo 6 teams erano riusciti ad attaccare CheesyCheats-2.

Al termine della gara questi risultati non sono variati di molto (4 attaccanti per CheesyCheats-1, 7 per CheesyCheats-2 e 6 per GabibbiTowers-1).

## GabbiTowers
_Categoria: crypto_

Gabibbi Tower è una piattaforma di gioco con ricompense.
Il gioco proposto consiste in due torri composte da caselle blu o rosse.
In cima alle torri ci sono due gabibbi, rispettivamente uno per ogni torre. La piattaforma fornisce due pulsanti: "blu" e "rosso".
Cliccando sul pulsante blu (o rosso), i gabibbi posizionati su una casella blu (o rossa) passano alla casella sottostante. Il gioco è considerato vinto se il gabibbi finiscono contemporaneamente le caselle a disposizione.
Le funzionalità messe a disposizione dalla piattaforma sono: registrazione, login, creazione una configurazione di gioco, disputa di una partita.

### GabibbiTowers-1
Per poter accedere alla prima vulnerabilità bisogna vincere una partita al gioco fornito dalla piattaforma. La vittoria fornisce un ticket. Con tre ticket si può richiedere la flag (un ticket può essere utilizzato per generare altri ticket). A fine giornata, il team ha provato a far arrivare i gabibbi insieme alla fine delle torri tramite algoritmi iterativi o di backtracking ma la stanchezza ha avuto la meglio e non si è riusciti a trovare una soluzione allo stesso tempo veloce e sempre funzionante.


### GabibbiTowers-2

#### Vulnerabilità - Incorrect Password Check
Analizzando il modulo storage abbiamo notato che esso presenta una vulnerabilità nel controllo della password.
I caratteri confrontati con quelli della password dell'utente sono, infatti, i primi n caratteri della stessa (con n = len della password inserita).
Per rompere la funzione di login, quindi, sarebbe bastato inviare una password vuota.

![gabibbi 2](imgs/gabibbi2.png)

#### Exploit
Quando è stato scritto l'exploit, tuttavia, si è pensato che una password vuota sarebbe stata l'attacco più ovvio (troppo facile da patchare).
Si è deciso, quindi, di provare ad indovinare il primo carattere della password, per non ricadere nel caso banale. Indovinare, in informatica, significa bruteforce:

![gabibbi 2](imgs/gabibbi2_exploit.png)

#### Patch
La patch per questo servizio prevede che la comparazione non sia fatta sui primi n caratteri della stringa ma su tutta la stringa. Bisogna quindi sostituire strlen(pass) con strlen(user.password)


## GadgetHorse-1

GadgetHorse è un'applicazione web, sviluppata col framework SvelteKit, che funge da e-commerce di sticker e magliette con stampe. 

![alt text](imgs/gadgethorse1.png)

Essa mette a disposizione alcune funzionalità come registrazione e login di utenti, acquisto di sticker predefiniti e creazione e acquisto di sticker e maglie personalizzate.

### Vulnerabilità - Unsigned Cookie

Questo primo flag store relativo a GadgetHorse, soffre di una vulnerabilità relativa al cookie del carrello. Lo stato del carrello veniva infatti memorizzato all'interno di un json, a sua volta salvato in un cookie che però non era firmato. Esso veniva solamente codificato in base64.

![alt text](imgs/gh1-cartcookie.png)

### Exploit

L'exploit costruito consisteva quindi nel creare un cookie custom del carrello inserendo un particolare id e trovando la flag nel prodotto - relativo a questo id - inserito nel carrello. Di seguito vediamo l'exploit nel dettaglio.

Inizialmente, per generare un po' di rumore e provare a confondere i teams avversari è stata prevista la registrazione di un utente random:

![alt text](imgs/register_gh.png)

In seguito, preso un determinato flagId, si considerava il "productId" lì presente, memorizzandolo nella variabile prodotto:

![alt text](imgs/gh_productid.png)

e si costruiva una lista, codificata in base64, relativa al carrello:

![alt text](imgs/gh_cartcookie.png)

a questo punto bastava fare una richiesta all'endpoint "/cart" con i cookies relativi a carrello e sessione e si trovava la flag:

![alt text](imgs/gh_flag.png)

### Patch

Per fixare questa vulnerabilità la soluzione ideale sarebbe stata quella di firmare il cookie del carrello. Tuttavia, per questioni di semplicità e velocità, (necessarie in questo tipo di competizione), la patch adottata è stata molto più semplice ma comunque altamente efficace. 

La soluzione attuata infatti prevedeva di rinominare il nome del cookie da "cart" a "cartone". Essa, come detto, si è rilevata una patch altamente efficace in quanto ci ha portato a non perdere alcuna flag su questo servizio. Questo perché tutti gli exploit consistevano nel prelevare i dati dal cookie denominato "cart", che però noi non fornivamo. Ovviamente, questa soluzione non ha dato fastidio al gameserver che, simulando i comportamenti legittimi, non aveva necessità di andare a considerare il cookie.

![alt text](imgs/gh1_patch.png)


## GadgetHorse-2

## MineCClicker
MineCClicker è una challenge della categoria pwn. E' una versione di prato fiorito. Viene fornito tramite un binario in C che rappresenta i server e un client scritto in Python. Il  servizio permetteva di fare le seguenti operazioni:

- Registrarsi e fare il login.
- Creare un boardgame: Nome, Secret(In questo campo sono messe le flag per i giochi forniti dal game server), seed, grandezza, numero di bombe
- Caricare una board
- Giocare alla board caricata.

![Gatto carino](imgs/giochino.png)

Ogni volta che un utente gioca una partita, le bombe vengono posizionate all'interno del tabellone in mod casuale, utilizzando due numeri come seme:
- Il seme scelto dal creatore della board.
- Un nuovo numero casuale fornito al giocatore.


I creatori del tabellone conoscono entrambi i semi, quindi possono rigenerare la disposizione casuale delle bombe e vincere sempre.

![Gatto carino](imgs/due.png)


Durante una partita, quando un utente trova la disposizione corretta delle bombe, vince la partita e ottiene il segreto.

Le flag sono memorizzate nel campo segreto di alcune board specifiche, create dal verificatore.

# Vulnerabilità - Giocare per sempre
Quando un utente scopre una cella e trova una bomba, il gioco dovrebbe terminare, ma il server non reimposta correttamente la variabile globale g_is_playing a false.

Le exploit sfruttato da molte altre squadre della cyberchallenge è il seguente:
- Scoprire celle casuali fino a trovare una bomba
- Leggere la disposizione delle bombe
- Inviare l'intera disposizione delle bombe al server e vincere la partita.

La squadra ha però notato che non c'era bisogno di trovare per forza una bomba per poter ricevere la board con la posizione delle bombe, ma bastava fare una singola richiesta al server su una casella scelta a caso per ricevere tutte le posizione delle bombe, così da non dover perdere, giocando in maniera lecit al gioco per poi ricevere le bombe. L'exploit illustrato nella figura viene spiegato in dettaglio commentando le linee di codice:

![Gatto carino](imgs/exploit.png)

La prima riga serve a prelevare il nome della board:

![Gatto carino](imgs/riga_uno.png)

La seconda riga, utilizzando le funzioni di utilità fornite dal client, inizializza una connessione con il server della macchina fornita in input:

![Gatto carino](imgs/riga_due.png)

La terza riga genera uno username casuale lungo 10 caratteri:

![Gatto carino](imgs/riga_tre.png)

La quarta riga genera una password casuale lungo 10 caratteri:

![Gatto carino](imgs/riga_quattro.png)

La riga cinque fa la registrazione dell'utente al server:

![Gatto carino](imgs/riga_cinque.png)

La riga sei fa il login alla piattraforma:

![Gatto carino](imgs/riga_sei.png)

La riga 7 carica la board:

![Gatto carino](imgs/riga_sette.png)

La riga 8,9 e 10 servono ad avviare il gioco con la board:

![Gatto carino](imgs/riga_otto.png)

Le restanti righe fanno la seguente operazione. Inviano una richiesta di uncover di una cella scelta a caso, questa restituiscela la board con la posizione delle bombe. Il for prende la board e dove ci sono le bombe mette le bandierine del prato fiorito, fatto ciò invia la board modificata al server che ovviamente considererà la board come vincente e restituirà la flag.

![Gatto carino](imgs/restanti.png)

Come si può facilmente evincere non c'è bisogno di perdere per poter ottenere la flag, ma basta seguire il procedimento descritto. Infatti questo attacco nonostante le patch degli avversari continuava a prendere le flag.

Per avviare l'exploit c'è bisogno di tutta la cartella client dato che utilizza le classi di utilità fornite per il client Python.

# Patch

Modificare il binario per reimpostare correttamente la variabile globale g_is_playing su false all'interno della funzione uncover, nel caso in cui si becca una.

![Gatto carino](imgs/patch.png)













## CheesyCheats
_Categorie: web/crypto/misc_

CheesyCheat è un’applicazione che si configura come shop di trucchi per videogiochi. Tramite un client messo a disposizione dal sistema di gioco è possibile vedere e comprare trucchi.
Inoltre, una parte dell’applicazione espone una VM che esegue codice nel linguaggio esoterico “Brain Fuck”.
La tecnologia alla base dell’applicazione è il framework gRPC: un framework di chiamate di procedura remota ad alte prestazioni open source multipiattaforma creato da Google.
La struttura dell’applicazione è divisa in tre sezioni principali: Client, API e Manager.
Il client può registrarsi all’applicazione, fare il login e vendere/comprare cheats.
Il Manager si occupa di gestire il login e la compravendita (a livello di db) dei cheats.
La sezione API, come da prassi, tutte le funzioni per far funzionare correttamente l’applicazione.

![architettura](./imgs/CheesyCheat0.png)

**Nell’analisi di questa challenge è bene specificare che, a causa dell’utilizzo del framework gRPC, i pcap non sono decifrabili in maniera tradizionale. Ricostruire un attacco è pressocché infattibile allo stato dell’arte.**
