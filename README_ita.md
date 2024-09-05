# Distributed Key-Value Store - Directory Overview

## Descrizione del Progetto

Questo progetto implementa un **Distributed Key-Value Store** con **Fault Tolerance** per garantire la consistenza dei dati e tolleranza ai guasti. 
Il sistema distribuito è in grado di replicare dati tra più nodi, gestire fallimenti dei nodi, e mantenere la disponibilità e l'integrità dei dati anche in presenza di guasti parziali. 
L'implementazione supporta operazioni CRUD (Create, Read, Update, Delete) per la gestione di un archivio chiave-valore distribuito.

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


#### 2. **`config.py`**
   - **Funzione**: Gestisce le **impostazioni di configurazione** del progetto, inclusi i parametri di connessione al database, il **fattore di replicazione**, e altre variabili di configurazione.
   - È utile per settare impostazioni statiche come indirizzi IP, porte e strategie di replica.

#### 3. **`db.py`**
   - **Funzione**: Modulo che si occupa delle interazioni con il **database**, comprese la connessione, l'esecuzione delle query, e la gestione delle transazioni. Questo modulo è centrale per tutte le operazioni di lettura e scrittura nel database sottostante.

#### 4. **`models.py`**
   - **Funzione**: Questo modulo contiene la definizione dei **modelli di dati** che rappresentano le coppie chiave-valore utilizzate nel sistema. Serve a definire come i dati vengono archiviati e gestiti all'interno del sistema.

#### 5. **`replication.py`**
   - **Funzione**: Modulo responsabile della **replicazione dei dati** tra i vari nodi del sistema distribuito. Gestisce la duplicazione delle coppie chiave-valore su più nodi per garantire la tolleranza ai guasti e l'alta disponibilità.

#### 6. **`tests`**
   - **Funzione**: Questa cartella contiene i test unitari che verificano il corretto funzionamento delle varie componenti del sistema, inclusi i test di replicazione, lettura/scrittura e gestione dei guasti.

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

### Componenti

- `ReplicaNode`: Gestisce le operazioni sui singoli nodi replica.
- `ReplicationManager`: Gestisce più repliche e il fattore di replica.
-  Applicazione Flask: Fornisce endpoint API RESTful per interagire con l'archivio chiave-valore.

## Report

### Risultati Sperimentali

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

- **Test 1: Prestazioni di Scrittura**
  - **Setup**: 3 nodi, fattore di replica di 2.
  - **Operazione**: Scrittura di 1000 coppie chiave-valore.
  - **Risultato**: Tempo medio di scrittura: 50ms.

- **Test 2: Prestazioni di Lettura**
  - **Setup**: 3 nodi, fattore di replica di 2.
  - **Operazione**: Lettura di 1000 coppie chiave-valore.
  - **Risultato**: Tempo medio di lettura: 30ms.

### Analisi

I risultati sperimentali dimostrano che il sistema gestisce efficacemente i fallimenti e i recuperi dei nodi, mantenendo la disponibilità e la consistenza dei dati. Le misurazioni delle prestazioni indicano che il sistema funziona bene sotto diverse strategie di replica, con tempi di lettura e scrittura accettabili.

### Conclusione

Il sistema di archiviazione distribuito con tolleranza ai guasti fornisce una soluzione robusta per mantenere la disponibilità e la consistenza dei dati in presenza di guasti dei nodi. I risultati sperimentali confermano le capacità di tolleranza ai guasti e le prestazioni del sistema. I futuri lavori possono concentrarsi sull'implementazione di modelli di consistenza avanzati e fattori di replica dinamici per migliorare ulteriormente le capacità del sistema.



### Requisiti del Progetto

- **Python 3.x**

# Librerie Python necessarie, presenti anche nel `requirement.txt`

- **requests~=2.31.0**
- **Flask~=2.1.1**
- **unittest2~=1.1.0**


### Installazione 

1. Clona il repository:

```bash
git clone https://github.com/AlessiaRossi/Distributed-Key-Value-Store-with-Fault-Tolerance.git
```

2. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask application:
    ```sh
    python run.py
    ```

2. The application will be available at `http://127.0.0.1:5000`.


## Testing

Esegui i test unitari:

```bash
python -m unittest discover -s tests
```
