// server_tcp.c - Server TCP Multi-Threaded in C (Jocul Mastermind)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define TCP_PORT 6006
#define BUFFER_SIZE 1024
#define MAX_INCERCARI 10

// Genereaz─â 4 cifre distincte (ex: "4815")
void genereaza_cod_secret(char *secret) {
    char cifre[] = "0123456789";
    for (int i = 9; i > 0; i--) {
        int j = rand() % (i + 1);
        char temp = cifre[i];
        cifre[i] = cifre[j];
        cifre[j] = temp;
    }
    strncpy(secret, cifre, 4);
    secret[4] = '\0';
}

// Verific─â dac─â ╚Öirul are exact 4 cifre distincte
int validare_incercare(const char *guess) {
    if (strlen(guess) != 4) return 0;
    for (int i = 0; i < 4; i++) {
        if (!isdigit(guess[i])) return 0;
        for (int j = i + 1; j < 4; j++) {
            if (guess[i] == guess[j]) return 0; // Cifre duplicate
        }
    }
    return 1;
}

// Thread-ul care gestioneaz─â un client TCP conectat
void* gestioneaza_client_tcp(void* arg) {
    int client_sock = *(int*)arg;
    free(arg);

    char secret[5];
    int incercari = 0;
    genereaza_cod_secret(secret);

    printf("[TCP THREAD %lu] Jucator nou conectat! Cod secret generat: %s\n", pthread_self(), secret);

    // Mesaj de bun venit
    const char *bun_venit = "START|Conectat la Serverul TCP in C (Ubuntu)! Ghiceste codul din 4 cifre distincte (10 incercari).";
    send(client_sock, bun_venit, strlen(bun_venit), 0);

    char buffer[BUFFER_SIZE];
    char raspuns[BUFFER_SIZE];

    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        int n = recv(client_sock, buffer, BUFFER_SIZE - 1, 0);
        if (n <= 0) {
            printf("[TCP THREAD %lu] Jucatorul s-a deconectat.\n", pthread_self());
            break;
        }

        // Elimin─âm newline/spa╚¢ii de la final
        buffer[strcspn(buffer, "\r\n")] = 0;
        printf("[TCP THREAD %lu] Primit: '%s'\n", pthread_self(), buffer);

        // Despachet─âm "COMANDA|VALOARE"
        char *comanda = strtok(buffer, "|");
        char *valoare = strtok(NULL, "|");
        if (!valoare) valoare = "";

        if (comanda && strcmp(comanda, "GUESS") == 0) {
            if (!validare_incercare(valoare)) {
                snprintf(raspuns, sizeof(raspuns), "EROARE|Introdu exact 4 cifre distincte (ex: 1234)!");
            } else {
                incercari++;
                int centrate = 0, mutate = 0;

                for (int i = 0; i < 4; i++) {
                    if (valoare[i] == secret[i]) {
                        centrate++;
                    } else if (strchr(secret, valoare[i]) != NULL) {
                        mutate++;
                    }
                }

                if (centrate == 4) {
                    snprintf(raspuns, sizeof(raspuns), 
                             "CASTIGAT|≡ƒÄë [C-SERVER] Ai spart codul (%s) din %d incercari! Am generat un cod nou.", 
                             secret, incercari);
                    genereaza_cod_secret(secret);
                    incercari = 0;
                    printf("[TCP THREAD %lu] Cod ghicit! Noul cod secret: %s\n", pthread_self(), secret);
                } else if (incercari >= MAX_INCERCARI) {
                    snprintf(raspuns, sizeof(raspuns), 
                             "PIERDUT|≡ƒÆÇ [C-SERVER] Ai ramas fara incercari! Codul era %s. Jocul a fost resetat.", 
                             secret);
                    genereaza_cod_secret(secret);
                    incercari = 0;
                    printf("[TCP THREAD %lu] Joc pierdut! Noul cod secret: %s\n", pthread_self(), secret);
                } else {
                    int ramase = MAX_INCERCARI - incercari;
                    snprintf(raspuns, sizeof(raspuns), 
                             "INFO|[%s] -> ≡ƒƒó %d Centrate | ≡ƒƒí %d Mutate (Mai ai %d incercari)", 
                             valoare, centrate, mutate, ramase);
                }
            }
            send(client_sock, raspuns, strlen(raspuns), 0);

        } else if (comanda && strcmp(comanda, "RESET") == 0) {
            genereaza_cod_secret(secret);
            incercari = 0;
            printf("[TCP THREAD %lu] Reset la cerere! Noul cod secret: %s\n", pthread_self(), secret);
            snprintf(raspuns, sizeof(raspuns), "INFO|≡ƒöä [C-SERVER] Jocul a fost resetat! Am generat un nou cod de 4 cifre.");
            send(client_sock, raspuns, strlen(raspuns), 0);

        } else if (comanda && strcmp(comanda, "EXIT") == 0) {
            break;
        }
    }

    close(client_sock);
    pthread_exit(NULL);
}

int main() {
    srand(time(NULL));
    int server_sock;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);

    if ((server_sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Eroare creare socket TCP");
        exit(EXIT_FAILURE);
    }

    // Permitem refolosirea imediat─â a portului dup─â ├«nchidere
    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(TCP_PORT);

    if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Eroare la bind TCP");
        close(server_sock);
        exit(EXIT_FAILURE);
    }

    if (listen(server_sock, 5) < 0) {
        perror("Eroare la listen TCP");
        close(server_sock);
        exit(EXIT_FAILURE);
    }

    printf("=== SERVER TCP (Joc Mastermind in C - Ubuntu) ===\n");
    printf("Asculta pe portul %d...\n", TCP_PORT);

    while (1) {
        int *client_sock = malloc(sizeof(int));
        *client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &addr_len);
        if (*client_sock < 0) {
            free(client_sock);
            continue;
        }

        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, gestioneaza_client_tcp, (void*)client_sock) == 0) {
            pthread_detach(thread_id);
        } else {
            perror("Eroare creare thread TCP");
            close(*client_sock);
            free(client_sock);
        }
    }

    close(server_sock);
    return 0;
}
