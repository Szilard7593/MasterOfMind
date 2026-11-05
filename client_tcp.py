import socket
from protocol import SERVER_IP, TCP_PORT, BUFFER_SIZE, impacheteaza_mesaj, despacheteaza_mesaj

class TCPClient:
    def __init__(self):
        self.sock = None
        self.conectat = False

    def conecteaza(self) -> tuple[bool, str]:
        self.inchide()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3.0)
            self.sock.connect((SERVER_IP, TCP_PORT))
            _, mesaj = despacheteaza_mesaj(self.sock.recv(BUFFER_SIZE))
            self.conectat = True
            return True, mesaj
        except Exception as e:
            self.conectat = False
            return False, f"[EROARE TCP] Nu mă pot conecta la {SERVER_IP}:{TCP_PORT}. Pornește ./server_tcp în Ubuntu!"

    def trimite_incercare(self, cifre: str) -> tuple[str, str]:
        if not self.conectat:
            ok, msg = self.conecteaza()
            if not ok:
                return "EROARE", msg
        try:
            self.sock.sendall(impacheteaza_mesaj("GUESS", cifre))
            return despacheteaza_mesaj(self.sock.recv(BUFFER_SIZE))
        except Exception as e:
            self.conectat = False
            return "EROARE", f"Conexiune întreruptă cu serverul C: {e}"

    def reseteaza_joc(self) -> tuple[str, str]:
        if not self.conectat:
            ok, msg = self.conecteaza()
            if not ok:
                return "EROARE", msg
        try:
            self.sock.sendall(impacheteaza_mesaj("RESET", ""))
            return despacheteaza_mesaj(self.sock.recv(BUFFER_SIZE))
        except Exception as e:
            self.conectat = False
            return "EROARE", f"Eroare comunicare: {e}"

    def inchide(self):
        if self.sock:
            try:
                if self.conectat:
                    self.sock.sendall(impacheteaza_mesaj("EXIT", ""))
                self.sock.close()
            except:
                pass
        self.sock = None
        self.conectat = False