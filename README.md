# 🌐 MasterOfMind – Sistem Client-Server Multi-Threaded (TCP & UDP)

**MasterOfMind** este o aplicație de rețea cross-platform care implementează o arhitectură **Client-Server bidirecțională** folosind protocoalele **TCP** și **UDP**. Proiectul combină performanța serverelor concurente scrise în **C (POSIX)** pe **Linux (Ubuntu)** cu o interfață grafică modernă dezvoltată în **Python (Tkinter)** pe **Windows**.

---

## ✨ Funcționalități Principale

### 1. 🎮 Jocul Mastermind în Rețea (Protocolul TCP – Port `6006`)
* **Sesiuni individuale orientate pe conexiune (Stateful):** La conectarea fiecărui client, serverul C generează în mod unic un cod secret format din **4 cifre distincte** (folosind algoritmul de amestecare *Fisher-Yates* și `rand_r` thread-safe).
* **Concurență Multi-Client:** Fiecare conexiune este preluată de un fir de execuție dedicat (`pthread`), permițând mai multor jucători să se joace simultan în ferestre separate fără interferențe.
* **Sistem de validare și indicii în timp real:**
  * Verifică la nivel de server dacă numărul introdus are exact 4 cifre unice.
  * Calculează și returnează numărul de cifre **Centrate (🟢)** (cifră corectă pe poziție exactă) și **Mutate (🟡)** (cifră corectă pe o altă poziție).
  * Gestionează automat numărul de încercări rămase (maxim 10), condițiile de victorie/înfrângere și resetarea jocului la cerere.

### 2. 🔐 Procesor Rapid de Șiruri de Caractere (Protocolul UDP – Port `5005`)
* **Comunicare rapidă fără conexiune (Stateless):** Fiecare pachet UDP este procesat independent pe un thread separat în serverul C și returnat instantaneu clientului.
* **3 Moduri de procesare disponibile din interfață:**
  1. **Inversare șir:** Inversează ordinea caracterelor (`Salut` $\rightarrow$ `tulaS`).
  2. **Amestecare (Shuffle):** Rearanjează aleatoriu literele din șir.
  3. **Criptare (Cifrul lui Cezar):** Criptează textul prin deplasarea literelor cu $+3$ poziții în alfabet (`abc` $\rightarrow$ `def`).

### 3. 🖥️ Interfață Grafică Modernă (GUI)
* Dezvoltată în **Tkinter** cu temă *Dark Mode* (`#1e1e2e`) și organizată în tab-uri (`ttk.Notebook`).
* Include consolă de istoric cu scroll automat pentru sesiunea TCP, scurtături din tastatură (`Enter` pentru trimitere rapidă) și buton de reconectare la server.

---

## 📂 Structura Proiectului

```text
MasterOfMind/
│
├── server_tcp.c        # Serverul TCP concurent în C (Jocul Mastermind - Port 6006)
├── server_udp.c        # Serverul UDP concurent în C (Procesare șiruri - Port 5005)
│
├── main.py             # Punctul de intrare al aplicației client (lansează GUI-ul)
├── ui.py               # Interfața grafică Tkinter (Tab-uri TCP & UDP)
├── client_tcp.py       # Modulul client TCP (gestionează conexiunea și comenzile jocului)
├── client_udp.py       # Modulul client UDP (trimite și primește datagramele procesate)
├── protocol.py         # Configurări IP/Porturi și serializarea pachetelor de rețea
│
├── game.py             # Implementare alternativă a logicii Mastermind în Python
└── network.py          # Server TCP alternativ în Python (pentru testare locală)
```

---

## 📡 Specificația Protocolului de Aplicație

Comunicarea între clientul Python și serverele C se realizează prin fluxuri de octeți codificate `UTF-8`, utilizând delimitatori clari:

### Protocolul TCP (`COMANDA|DATE`)
* **Conectare inițială:** Serverul trimite `START|<Mesaj de bun venit>`
* **Trimitere încercare:** Clientul trimite `GUESS|1234` $\rightarrow$ Serverul răspunde cu:
  * `INFO|[1234] -> 🟢 X Centrate | 🟡 Y Mutate (Mai ai Z incercari)`
  * `CASTIGAT|<Mesaj victorie + regenerare cod>`
  * `PIERDUT|<Mesaj final + dezvăluire cod secret>`
  * `EROARE|<Mesaj validare input>`
* **Resetare rundă:** Clientul trimite `RESET|` $\rightarrow$ Serverul regenerează codul și răspunde cu `INFO|<Confirmare>`
* **Deconectare:** Clientul trimite `EXIT|`

### Protocolul UDP (`OPTIUNE:TEXT`)
* Clientul trimite o datagramă de forma `1:Retele`, `2:Retele` sau `3:Retele`.
* Serverul C extrage prefixul opțiunii, aplică algoritmul corespunzător și returnează șirul transformat.

---

## 🚀 Instrucțiuni de Compilare și Rulare

### Pasul 1: Pornirea Serverelor în C (pe Ubuntu / WSL2)

1. Deschide terminalul Ubuntu și verifică adresa IP a interfeței de rețea (`eth0`):
   ```bash
   ip a
   ```
2. Compilează cele două servere folosind `gcc` cu suportul pentru fire de execuție POSIX (`-pthread`):
   ```bash
   gcc -Wall -pthread server_udp.c -o server_udp
   gcc -Wall -pthread server_tcp.c -o server_tcp
   ```
3. Pornește ambele servere (poți rula serverul UDP în fundal și cel TCP în prim-plan pentru a urmări log-urile):
   ```bash
   ./server_udp &
   ./server_tcp
   ```

### Pasul 2: Configurarea și Pornirea Clientului (pe Windows)

1. Verifică fișierul `protocol.py` și asigură-te că variabila `SERVER_IP` conține adresa IP a mașinii Ubuntu (de exemplu, `172.30.118.143`):
   ```python
   SERVER_IP = '172.30.118.143'
   TCP_PORT = 6006
   UDP_PORT = 5005
   ```
2. Pornește aplicația grafică rulând `main.py` din PyCharm sau din terminalul Windows:
   ```powershell
   py main.py
   ```
   *(Poți rula comanda `py main.py` în mai multe terminale simultan pentru a deschide mai multe instanțe de client și a juca în paralel).*