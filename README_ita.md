# Distributed Key-Value Store - Directory Overview

## Descrizione del Progetto

Questo progetto implementa un **Distributed Key-Value Store** con **Fault Tolerance** per garantire la consistenza dei dati e tolleranza ai guasti. Il sistema distribuito è in grado di replicare dati tra più nodi, gestire fallimenti dei nodi, e mantenere la disponibilità e l'integrità dei dati anche in presenza di guasti parziali. L'implementazione supporta operazioni CRUD (Create, Read, Update, Delete) per la gestione di un archivio chiave-valore distribuito.

### Obiettivi principali del progetto:

- Garantire **alta disponibilità** dei dati attraverso la replica su più nodi.
- Mantenere la **consistenza dei dati** tra i nodi.
- Implementare una gestione efficace della **tolleranza ai guasti**.

## Caratteristiche Principali

- **Tolleranza ai guasti**: il sistema continua a funzionare anche in presenza di guasti.
- **Distribuzione dei dati**: replica dei dati su più nodi per garantire disponibilità.
- **Consistenza**: evita disallineamenti nei dati.
- **Operazioni su un archivio chiave-valore**: tramite operazioni CRUD è possibile inserire, aggiornare, eliminare e recuperare valori.
- **Scalabilità**: possibilità di aggiungere nuovi nodi per aumentare la capacità del sistema.

### Contenuto delle Cartelle e File del branch `main`

#### 1. **`app.py`**  
   - **Funzione**: Questo file contiene la logica principale del **server web** e gestisce l'interfaccia per il **database distribuito**.
   - Viene utilizzato per avviare l'applicazione e interagire con le varie componenti del sistema distribuito.

   In `app.py` sono contenuti i seguenti moduli:

   #### `__init__.py`
   Viene definita una funzione `create_app()` che crea e configura un'applicazione Flask.

   #### `consistent_app.py`
   Si implementa una classe chiamata `ConsistentHash` che utilizza un meccanismo di consistent hashing per distribuire le chiavi su una serie di nodi in modo bilanciato. Il consistent hashing è una tecnica utilizzata per distribuire oggetti su più nodi in modo che quando i nodi vengono aggiunti o rimossi, solo una piccola parte degli oggetti deve essere spostata tra i nodi, piuttosto che ridistribuire tutto.

   #### `models.py`
   Il codice che hai fornito implementa un sistema di replica distribuita per un archivio di chiavi-valore (Key-Value Store) con supporto per la tolleranza ai guasti. Il sistema permette di distribuire e replicare dati su più nodi e di gestire il fallimento e il recupero dei nodi in modo trasparente. In questa fase del progetto si crea il db con `def _initialize_db(self):`

   Vediamo le funzionalità principali delle due classi, `ReplicaNode` e `ReplicationManager`, che costituiscono il nucleo del sistema:

   **ReplicaNode**:

   Ogni `ReplicaNode` rappresenta un singolo nodo nel sistema distribuito, con un database SQLite locale per archiviare coppie chiave-valore. I nodi supportano:
   - Scrittura e lettura di coppie chiave-valore
   - Simulazione di guasti e ripristino
   - Sincronizzazione dei dati con altri nodi attivi durante il ripristino

   **ReplicationManager**:

   `ReplicationManager` gestisce la strategia di replica su più nodi. Supporta:
   - Scrittura su e lettura da tutti i nodi (replica completa) o nodi specifici (hashing coerente)
   - Simulazione di guasti e ripristino dei nodi
   - Garanzia di coerenza dei dati tra i nodi attivi

   #### `routes.py`
   Il modulo si articola con:

   1. **Autenticazione API**: Ogni richiesta deve includere un token API valido nell'header `Authorization` per essere autorizzata. Se il token è invalido, la richiesta viene respinta.

   2. **Scrittura di Dati** (`/write` - POST): Consente di scrivere una coppia chiave-valore nel sistema distribuito, replicando i dati sui nodi attivi.

   3. **Lettura di Dati** (`/read/<key>` - GET): Consente di leggere il valore associato a una chiave specifica dai nodi attivi.

   4. **Cancellazione di Dati** (`/delete/<key>` - DELETE): Permette di eliminare una chiave e il relativo valore dal sistema distribuito.

   5. **Simulazione di Fallimento Nodo** (`/fail/<int:node_id>` - POST): Simula il fallimento di un nodo specifico per testare la tolleranza ai guasti del sistema.

   6. **Recupero Nodo** (`/recover/<int:node_id>` - POST): Recupera un nodo fallito e lo sincronizza con i nodi attivi.

   7. **Visualizzazione Stato Nodi** (`/nodes` - GET): Restituisce lo stato attuale (attivo/inattivo) di tutti i nodi nel sistema.

   8. **Impostazione della Strategia di Replica** (`/set_replication_strategy` - POST): Consente di impostare la strategia di replica del sistema (replica completa o hashing consistente).

   9. **Recupero dei Nodi per una Chiave** (`/nodes_for_key/<key>` - GET): Restituisce i nodi responsabili di una chiave specifica (solo per l'hashing consistente).

   Struttura Generale:
   - **API Token**: Verifica il token di autenticazione nelle richieste.
   - **Manager di Replica**: Ogni operazione viene gestita dal `ReplicationManager` che coordina la replicazione dei dati e la tolleranza ai guasti.
   - **Risposte dell'API**: Tutte le risposte sono strutturate in formato JSON con un messaggio di successo o errore.

#### 2. **`tests`**
   - **Funzione**: Questa cartella contiene i test unitari che verificano il corretto funzionamento delle varie componenti del sistema, inclusi i test di replicazione, lettura/scrittura e gestione dei guasti.

#### 3. **`.gitignore`**
   - Definisce i file e le cartelle da ignorare nel repository Git.

#### 4. **`client.py`**
   - **Funzione**: Modulo che si occupa delle interazioni con il **database**, comprese la connessione, l'esecuzione delle query, e la gestione delle transazioni. Questo modulo è centrale per tutte le operazioni di lettura e scrittura nel database sottostante. Questa sezione definisce un client per interagire con un sistema distribuito di archiviazione chiave-valore (Distributed Key-Value Store). Ecco le principali funzionalità del client:

   1. **Inizializzazione**: 
   - Il client viene inizializzato con l'URL del server e un token API per autenticazione.
   
   2. **Funzioni di scrittura e lettura**: 
   - `write(key, value)`: Scrive una coppia chiave-valore nel sistema distribuito.
   - `read(key)`: Legge il valore associato a una chiave specifica.

   3. **Funzioni di cancellazione e verifica nodo**:
   - `delete(key)`: Cancella una coppia chiave-valore.
   - `fail_node(node_id)`: Simula il fallimento di un nodo specifico.
   - `recover_node(node_id)`: Recupera un nodo specifico.

   4. **Funzioni di gestione della replica**:
   - `set_replication_strategy(strategy, replication_factor)`: Imposta la strategia di replica (es. full o consistent).
   - `get_nodes()`: Recupera lo stato di tutti i nodi nel sistema.

   5. **Dimostrazione di fail-recover**: 
   - `demonstrate_fail_recover_behavior()`: Mostra come il sistema gestisce il fallimento e il recupero di nodi.

   L'interfaccia consente di eseguire queste azioni attraverso un menu a scelta, facilitando l'interazione con il sistema distribuito.

#### 5. **`design_document.md`**
   - Questo modulo espone in maniera chiara e grafica la ripartizione del progetto e delle principali funzionalità.

#### 6. **`report.md`**
   - Fornisce le principali riflessioni e risultati ottenuti con il progetto.

#### 7. **`requirements.txt`**
   - Si riportano tutte i requirements per runnare e poter usare il programma.

#### 8. **`run.py`**
   - Si eseguono test automatici per verificare il corretto funzionamento di un sistema di **Distributed Key-Value Store** utilizzando Flask e il framework di test Python `unittest`.

   ## Componenti principali:

   1. **Setup dell'applicazione**:
   - Viene creato un client di test dell'applicazione Flask per simulare richieste HTTP verso l'applicazione.

   2. **Test delle operazioni di scrittura e lettura**:
   - Scrittura di una coppia chiave-valore (`key1`, `value1`) e verifica della possibilità di leggerla correttamente.

   3. **Test di fallimento e recupero dei nodi**:
   - Simula il fallimento di un nodo, verifica la disponibilità dei dati sulle altre repliche e il recupero corretto del nodo fallito.

   4. **Test di fallimento di tutte le repliche**:
   - Fallimento di tutte le repliche, verifica del fallimento nella lettura e successivo recupero dei dati dopo la riattivazione di una replica.

   ## Funzione principale:
  - Se lo script viene eseguito con l'argomento "test", vengono eseguiti i test con `unittest`.
  - Se eseguito normalmente, l'applicazione Flask viene avviata in modalità debug.

---

### Gestione delle richieste client-server 
## API Endpoints

- `POST /write`: Scrive una coppia chiave-valore.
- `GET /read/<key>`: Legge un valore tramite la chiave.
- `DELETE /delete/<key>`: Elimina una coppia chiave-valore.
- `POST /fail/<int:node_id>`: Simula un fallimento di un nodo.
- `POST /recover/<int:node_id>`: Recupera un nodo fallito.
- `GET /nodes`: Ottiene lo stato di tutti i nodi.

### Architettura del Sistema

Il sistema è composto da più nodi replica gestiti da un manager di replicazione. Ogni nodo è un'istanza della classe `ReplicaNode`, che gestisce operazioni individuali come lettura, scrittura e eliminazione. La classe `ReplicationManager` gestisce questi nodi e garantisce la replicazione dei dati tra loro.

### Componenti principali 

- `ReplicaNode`: Gestisce le operazioni sui singoli nodi replica.
- `ReplicationManager`: Gestisce più repliche e il fattore di replica.
- Applicazione Flask: Fornisce endpoint API RESTful per interagire con l'archivio chiave-valore.

#### Test di Tolleranza ai Guasti

Abbiamo condotto una serie di test per valutare le capacità di tolleranza ai guasti del sistema. I test hanno coinvolto la simulazione di fallimenti e recuperi dei nodi durante le operazioni di lettura e scrittura. I risultati hanno mostrato che il sistema ha mantenuto con successo la disponibilità e la consistenza dei dati durante i fallimenti e i recuperi dei nodi.

- **Test 1: Fallimento di un Singolo Nodo**
  - **Setup**: 3 nodi, fattore di replica di 2.
  - **Operazione**: Scrittura di 10 coppie chiave-valore, fallimento di 1 nodo, lettura di tutte le coppie chiave-valore.
  - **Risultato**: Tutte le coppie chiave-valore erano disponibili dagli altri nodi.

- **Test 2: Fallimento di Più Nodi**
  - **Setup**: 5 nodi, fattore di replica di 3.
  - **Operazione**: Scrittura di 20 coppie chiave-valore, fallimento di 2 nodi, lettura di tutte le coppie chiave-valore.
  - **Risultato**: Tutte le coppie chiave-valore erano disponibili dagli altri nodi.

- **Test 3: Recupero di un Nodo**
  - **Setup**: 3 nodi, fattore di replica di 2.
  - **Operazione**: Scrittura di 10 coppie chiave-valore, fallimento di 1 nodo, recupero del nodo, lettura di tutte le coppie chiave-valore.
  - **Risultato**: Il nodo recuperato ha sincronizzato i dati e tutte le coppie chiave-valore erano disponibili.

### Misurazioni delle Prestazioni

Abbiamo misurato le prestazioni del sistema sotto diverse strategie di replica. I test hanno coinvolto la scrittura e lettura di un gran numero di coppie chiave-valore e la misurazione del tempo impiegato per ciascuna operazione.

### Performance Measurement

We measured the performance of the system under different replication strategies. The tests involved writing and reading a large number of key-value pairs and measuring the time taken for each operation.

- **Test 1: Risultati Consistent Strategy**
  - **Fail**: 0,0200 s
  - **Recover**: 0,0100 s
  - **Read**: 0,0105 s
  - **Write**: 0,1703

- **Test 2: Risultati Fail/Recover Full Strategy**
 ??

- **Test 3: Risultati Full Strategy**
  - **Fail**: 0,0000 s
  - **Recover**: 0,2274 s
  - **Read**: 0,0000 s
  - **Write**: 0,1118 s


 **Total test** : 1.090 s (6 test)

### Analisi

I risultati sperimentali dimostrano che il sistema gestisce efficacemente i fallimenti e i recuperi dei nodi, mantenendo la disponibilità e la consistenza dei dati. Le misurazioni delle prestazioni indicano che il sistema funziona bene sotto diverse strategie di replica, con tempi di lettura e scrittura accettabili.

### Conclusione

Il sistema di archiviazione distribuito con tolleranza ai guasti fornisce una soluzione robusta per mantenere la disponibilità e la consistenza dei dati in presenza di guasti dei nodi. I risultati sperimentali confermano le capacità di tolleranza ai guasti e le prestazioni del sistema. I futuri lavori possono concentrarsi sull'implementazione di modelli di consistenza avanzati e fattori di replica dinamici per migliorare ulteriormente le capacità del sistema.

### Requisiti del Progetto

- **Python 3.x**

# Librerie Python necessarie, presenti anche nel `requirements.txt`

- **requests~=2.31.0**
- **Flask~=2.1.1**
- **unittest2~=1.1.0**

### Installazione 

1. Clona il repository:

   ```bash
   git clone https://github.com/AlessiaRossi/Distributed-Key-Value-Store-with-Fault-Tolerance.git 
   

 2. Installa le dipendenze:

   ```bash
     pip install -r requirements.txt
   ```

## Running del programma

1. Start the Flask application:
    ```sh
    python run.py
    ```

2. The application will be available at `http://127.0.0.1:5000`.


## Testing

Esegui i test unitari:

```bash
python -m unittest test_performance.py
```
