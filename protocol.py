SERVER_IP = '172.30.118.143'  # IP-ul din Ubuntu (WSL)
TCP_PORT = 6006               # Portul pentru jocul Mastermind (TCP)
UDP_PORT = 5005               # Portul pentru procesarea de șiruri (UDP)
BUFFER_SIZE = 1024

def impacheteaza_mesaj(comanda: str, date: str = "") -> bytes:
    """Formatează mesajul TCP sub forma COMANDA|DATE"""
    return f"{comanda}|{date}".encode('utf-8')

def despacheteaza_mesaj(raw_bytes: bytes) -> tuple[str, str]:
    """Despachetează răspunsul TCP primit de la serverul în C"""
    text = raw_bytes.decode('utf-8', errors='replace').strip()
    if "|" in text:
        comanda, date = text.split("|", 1)
        return comanda, date
    return "INFO", text