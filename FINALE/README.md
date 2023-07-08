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

## GabibbiTowers-2

## GadgetHorse-1

## GadgetHorse-2

## MineCClicker

## CheesyCheats
CheesyCheat è un’applicazione che si configura come shop di trucchi per videogiochi. Tramite un client messo a disposizione dal sistema di gioco è possibile vedere e comprare trucchi.
Inoltre, una parte dell’applicazione espone una VM che esegue codice nel linguaggio esoterico “Brain Fuck”.
La tecnologia alla base dell’applicazione è il framework gRPC: un framework di chiamate di procedura remota ad alte prestazioni open source multipiattaforma creato da Google.
La struttura dell’applicazione è divisa in tre sezioni principali: Client, API e Manager.
Il client può registrarsi all’applicazione, fare il login e vendere/comprare cheats.
Il Manager si occupa di gestire il login e la compravendita (a livello di db) dei cheats.
La sezione API, come da prassi, tutte le funzioni per far funzionare correttamente l’applicazione.

![architettura](./imgs/CheesyCheat0.png)

Nella sezione flagIds della piattaforma di gioco era presente l’username di un utente. Questo ci fa capire che, probabilmente, bisognerà accedere al suo account.

La vulnerabilità legata a questo indizio consiste nel processo di autenticazione.
Questo si basa su un protocollo che ricorda il Diffie Hellman ma che non funziona allo stesso modo. Questo, infatti, serve a generare una di una chiave di autenticazione che sia legata alla password dell’utente e che sia uguale sia sul client che sul server. Il problema sorge nel modo di generare la chiave. K, infatti, è definita come:

_K = pow(int(request.g_a, 16), b, utils.p)_

E, impostando g_a uguale a 0, si ottiene K=0.

La mitigazione a questo errore la si ottiene imponendo che g_a non debba ricadere nei casi banali dell’elevamento a potenza.

**Nell’analisi di questa challenge è bene specificare che, a causa dell’utilizzo del framework gRPC, i pcap non sono decifrabili in maniera tradizionale. Quindi ricostruire un attacco è pressocché infattibile allo stato dell’arte.**
