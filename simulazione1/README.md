## CCMarket
![Gatto carino](img/logo.png)
CCMarket è una challenge di pwn. In CCmarket dopo aver fatto l'accesso si ha disposizione una quota di soldi per acquistare oggetti e si può scegliere se accettare gli oggetti sul mercato oppure se creare oggetti da mettere sul mercato. Se acquistiamo gli oggetti forniti nei flagID si ottengono le flag, ovviamente non abbiamo a disposizione abbastanza soldi per acquistare i flagID, dato che il loro prezzo è MAX_INT di C. 




### Vulnerabilità - Si può generare un prezzo negativo
Il problema è che CCMArket da la possibilità di aggiungere sul mercato oggetti che hanno un prezzo negativo. Ci da la possibilità ce quando acquistiamo un oggetto otteniamo soldi invece che perderne.

Viene illustrato l'exploit.

In questa prima fase si interagisce con il servizio, facendo una registrazione di un utente e facendo il login.

![Gatto carino](img/1.png)

Nella seconda fase si aggiunge l'oggetto con prezzo -MAX_INT sul mercato.

![Gatto carino](img/2.png)

Nella terza fase compriamo l'oggetto con prezzo negativo

![Gatto carino](img/3.png)

Nella quarta ed ultima fase compriamo l'oggetto con dentro la flag e ne analizziamo il contenuto per ottenere la flag.

![Gatto carino](img/4.png)




### Patch
Una patch che era possibile implementare era quella di verificare che un oggetto da immettere sul mercato potesse avere solo un prezzo positivo. Modificando questa funzione:

![Gatto carino](img/funzione.png)

Andando a modificare la funzione **strncpy** con il metodo del PRELOADING e inserendo all'interno della funzione una verifica sul prezzo. Questo metodo non era però noto al tempo della simulazione quindi non si è riusciti a patchare.



