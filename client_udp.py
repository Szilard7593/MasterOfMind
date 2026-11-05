import socket
from protocol import SERVER_IP, UDP_PORT, BUFFER_SIZE

class UDPClient:
    @staticmethod
    def proceseaza_sir(optiune: str, text: str) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        try:
            mesaj = f"{optiune}:{text}"
            sock.sendto(mesaj.encode('utf-8'), (SERVER_IP, UDP_PORT))
            data, _ = sock.recvfrom(BUFFER_SIZE)
            return data.decode('utf-8', errors='replace')
        except socket.timeout:
            return f"[EROARE UDP] Serverul C de pe Ubuntu ({SERVER_IP}:{UDP_PORT}) nu răspunde! Verifică dacă ./server_udp este pornit."
        except Exception as e:
            return f"[EROARE UDP]: {e}"
        finally:
            sock.close()

if __name__ == "__main__":
    print("=== TEST CONSOLĂ CLIENT UDP ===")
    while True:
        opt = input("Opțiune (1-Invers, 2-Amestecat, 3-Criptat, exit): ").strip()
        if opt == "exit":
            break
        txt = input("Text: ").strip()
        print(UDPClient.proceseaza_sir(opt, txt), "\n")