import tkinter as tk
from tkinter import ttk, scrolledtext
from client_tcp import TCPClient
from client_udp import UDPClient

class ReteleAppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Python (Windows) <---> Server C (Ubuntu)")
        self.root.geometry("700x520")
        self.root.configure(bg="#1e1e2e")

        self.tcp_client = TCPClient()

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 10, 'bold'))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_tcp = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab_udp = tk.Frame(self.notebook, bg="#1e1e2e")

        self.notebook.add(self.tab_tcp, text=" Joc Mastermind (TCP -> C Ubuntu)")
        self.notebook.add(self.tab_udp, text=" Procesare Șiruri (UDP -> C Ubuntu)")

        self._construieste_tab_tcp()
        self._construieste_tab_udp()

        self.root.protocol("WM_DELETE_WINDOW", self.la_inchidere)

    def _construieste_tab_tcp(self):
        tk.Label(self.tab_tcp, text="SPĂRGĂTORUL DE CODURI", fg="#a6e3a1", bg="#1e1e2e",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.log_tcp = scrolledtext.ScrolledText(self.tab_tcp, height=14, width=75, bg="#11111b",
                                                 fg="#cdd6f4", font=("Consolas", 10))
        self.log_tcp.pack(padx=15, pady=5)

        frame_input = tk.Frame(self.tab_tcp, bg="#1e1e2e")
        frame_input.pack(pady=12)

        tk.Label(frame_input, text="Cod (4 cifre):", fg="white", bg="#1e1e2e", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        self.entry_tcp = tk.Entry(frame_input, font=("Consolas", 13), width=10, justify='center')
        self.entry_tcp.pack(side=tk.LEFT, padx=5)
        self.entry_tcp.bind('<Return>', lambda e: self.trimite_tcp())

        tk.Button(frame_input, text="Trimite", bg="#89b4fa", fg="#11111b", font=("Segoe UI", 10, "bold"),
                  command=self.trimite_tcp).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_input, text="Reset Joc", bg="#f38ba8", fg="#11111b", font=("Segoe UI", 10, "bold"),
                  command=self.reset_tcp).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_input, text="Reconectare Server", bg="#fab387", fg="#11111b", font=("Segoe UI", 10, "bold"),
                  command=self.conecteaza_tcp).pack(side=tk.LEFT, padx=5)

        self.conecteaza_tcp()

    def conecteaza_tcp(self):
        ok, msg = self.tcp_client.conecteaza()
        self.log_tcp.insert(tk.END, f"{msg}\n" + "-"*68 + "\n")
        self.log_tcp.see(tk.END)

    def trimite_tcp(self):
        val = self.entry_tcp.get().strip()
        if not val:
            return
        self.entry_tcp.delete(0, tk.END)
        _, raspuns = self.tcp_client.trimite_incercare(val)
        self.log_tcp.insert(tk.END, f"{raspuns}\n")
        self.log_tcp.see(tk.END)

    def reset_tcp(self):
        _, raspuns = self.tcp_client.reseteaza_joc()
        self.log_tcp.insert(tk.END, f"\n{raspuns}\n" + "-"*68 + "\n")
        self.log_tcp.see(tk.END)

    def _construieste_tab_udp(self):
        tk.Label(self.tab_udp, text="PROCESARE ȘIRURI PRIN UDP", fg="#f9e2af", bg="#1e1e2e",
                 font=("Segoe UI", 13, "bold")).pack(pady=15)

        tk.Label(self.tab_udp, text="Introdu șirul de caractere:", fg="white", bg="#1e1e2e", font=("Segoe UI", 11)).pack()
        self.entry_udp = tk.Entry(self.tab_udp, font=("Consolas", 12), width=45)
        self.entry_udp.pack(pady=8)
        self.entry_udp.insert(0, "ReteleDeCalculatoare")

        self.optiune_udp = tk.StringVar(value="1")
        frame_radio = tk.Frame(self.tab_udp, bg="#1e1e2e")
        frame_radio.pack(pady=5)

        optiuni = [("1 - Inversează", "1"), ("2 - Amestecă literele", "2"), ("3 - Criptează (Cezar)", "3")]
        for text, val in optiuni:
            tk.Radiobutton(frame_radio, text=text, variable=self.optiune_udp, value=val,
                           bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)

        tk.Button(self.tab_udp, text="Trimite Pachet UDP către Ubuntu", bg="#a6e3a1", fg="#11111b",
                  font=("Segoe UI", 11, "bold"), command=self.trimite_udp).pack(pady=12)

        self.lbl_raspuns_udp = tk.Label(self.tab_udp, text="Răspunsul serverului C va apărea aici...",
                                        fg="#89dceb", bg="#11111b", font=("Consolas", 11), width=62, height=5, wraplength=520)
        self.lbl_raspuns_udp.pack(pady=10, padx=15)

    def trimite_udp(self):
        text = self.entry_udp.get().strip()
        opt = self.optiune_udp.get()
        if not text:
            return
        raspuns = UDPClient.proceseaza_sir(opt, text)
        self.lbl_raspuns_udp.config(text=raspuns)

    def la_inchidere(self):
        self.tcp_client.inchide()
        self.root.destroy()