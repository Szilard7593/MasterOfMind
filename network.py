# network.py
import socket
import threading
from protocol import TCP_HOST, TCP_PORT, BUFFER_SIZE, impacheteaza_mesaj, despacheteaza_mesaj
from game import MastermindGame

def gestioneaza_client_tcp(conn: socket.socket, addr):
    print(f"[SERVER TCP - THREAD {threading.get_ident()}] Jucător nou conectat: {addr}")
    joc = MastermindGame()
    print(f"[DEBUG SERVER] Codul secret pentru {addr} este: {joc.secret}")

    # Trimitem mesajul de bun venit la conectare
    bun_venit = "Conectat la Serverul TCP! Ghicește codul din 4 cifre distincte (ai 10 încercări)."
    conn.sendall(impacheteaza_mesaj("START", bun_venit))

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            comanda, valoare = despacheteaza_mesaj(data)
            print(f"[TCP {addr}] Comandă: {comanda} | Valoare: {valoare}")

            if comanda == "GUESS":
                status, mesaj = joc.verifica_incercare(valoare)
                conn.sendall(impacheteaza_mesaj(status, mesaj))
            elif comanda == "RESET":
                joc.reset_game()
                print(f"[DEBUG SERVER] Cod nou pentru {addr}: {joc.secret}")
                conn.sendall(impacheteaza_mesaj("INFO", "🔄 Jocul a fost resetat! Am generat un nou cod de 4 cifre."))
            elif comanda == "EXIT":
                break
    except ConnectionResetError:
        pass
    finally:
        print(f"[SERVER TCP] Jucătorul {addr} s-a deconectat.")
        conn.close()

def porneste_server_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(5)
    print(f"=== SERVER TCP (Mastermind) pornit pe {TCP_HOST}:{TCP_PORT} ===")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=gestioneaza_client_tcp, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nOprire server TCP...")
    finally:
        server.close()

if __name__ == "__main__":
    porneste_server_tcp()