# game.py
import random

class MastermindGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        # Generăm 4 cifre distincte (ex: "4815")
        cifre = random.sample("0123456789", 4)
        self.secret = "".join(cifre)
        self.incercari = 0
        self.max_incercari = 10

    def verifica_incercare(self, guess: str) -> tuple[str, str]:
        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            return "EROARE", "Introdu exact 4 cifre distincte (ex: 1234)!"

        self.incercari += 1
        centrate = sum(1 for i in range(4) if guess[i] == self.secret[i])
        mutate = sum(1 for i in range(4) if guess[i] in self.secret and guess[i] != self.secret[i])

        if centrate == 4:
            secret_vechi = self.secret
            incercari_facute = self.incercari
            self.reset_game()
            return "CASTIGAT", f" Ai spart codul ({secret_vechi}) din {incercari_facute} încercări! Am generat un cod nou."

        if self.incercari >= self.max_incercari:
            secret_vechi = self.secret
            self.reset_game()
            return "PIERDUT", f" Ai rămas fără încercări! Codul era {secret_vechi}. Jocul a fost resetat."

        ramase = self.max_incercari - self.incercari
        return "INFO", f"[{guess}] -> >< {centrate} Centrate | <> {mutate} Mutate (Mai ai {ramase} încercări)"