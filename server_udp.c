// server_udp.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define PORT 5005
#define BUFFER_SIZE 1024

// Structur─â pentru a trimite datele c─âtre thread-ul de procesare
typedef struct {
    int sockfd;
    struct sockaddr_in client_addr;
    socklen_t addr_len;
    char buffer[BUFFER_SIZE];
} client_request_t;

// 1. Func╚¢ie pentru inversarea ╚Öirului
void inverseaza_sir(char *str) {
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - i - 1];
        str[len - i - 1] = temp;
    }
}

// 2. Func╚¢ie pentru amestecarea literelor (Shuffle)
void amesteca_sir(char *str) {
    int len = strlen(str);
    for (int i = len - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        char temp = str[i];
        str[i] = str[j];
        str[j] = temp;
    }
}

// 3. Func╚¢ie pentru Criptare Cezar (+3)
void cripteaza_cezar(char *str, int shift) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (isalpha(str[i])) {
            char baza = isupper(str[i]) ? 'A' : 'a';
            str[i] = (str[i] - baza + shift) % 26 + baza;
        }
    }
}

// Func╚¢ia executat─â concurent de fiecare thread
void* proceseaza_cerere(void* arg) {
    client_request_t *req = (client_request_t*)arg;
    char raspuns[BUFFER_SIZE + 64];
    
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(req->client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    
    printf("[THREAD %lu] Pachet primit de la %s:%d -> '%s'\n", 
           pthread_self(), client_ip, ntohs(req->client_addr.sin_port), req->buffer);

    // Formatul a╚Öteptat de la Python: "OPTIUNE:Text" (ex: "1:Salut")
    char optiune = req->buffer[0];
    char *text = req->buffer;
    
    if (strlen(req->buffer) > 2 && req->buffer[1] == ':') {
        text = req->buffer + 2; // S─ârim peste "1:"
    }

    char rezultat[BUFFER_SIZE];
    strncpy(rezultat, text, BUFFER_SIZE);

    if (optiune == '1') {
        inverseaza_sir(rezultat);
        snprintf(raspuns, sizeof(raspuns), "[C-SERVER INVERSAT]: %s", rezultat);
    } else if (optiune == '2') {
        amesteca_sir(rezultat);
        snprintf(raspuns, sizeof(raspuns), "[C-SERVER AMESTECAT]: %s", rezultat);
    } else if (optiune == '3') {
        cripteaza_cezar(rezultat, 3);
        snprintf(raspuns, sizeof(raspuns), "[C-SERVER CRIPTAT]: %s", rezultat);
    } else {
        snprintf(raspuns, sizeof(raspuns), "[C-SERVER EROARE]: Optiune necunoscuta.");
    }

    // Trimitem r─âspunsul ├«napoi la clientul Python (Bidirec╚¢ional)
    sendto(req->sockfd, raspuns, strlen(raspuns), 0, 
           (struct sockaddr*)&(req->client_addr), req->addr_len);

    free(req); // Eliber─âm memoria alocat─â pentru aceast─â cerere
    pthread_exit(NULL);
}

int main() {
    srand(time(NULL));
    int sockfd;
    struct sockaddr_in server_addr;

    // Creare socket UDP
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Eroare la crearea socket-ului");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY; // Ascult─â pe toate interfe╚¢ele de re╚¢ea
    server_addr.sin_port = htons(PORT);

    // Legare socket (Bind)
    if (bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Eroare la bind");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("=== SERVER UDP (Limbajul C - Ubuntu) ===\n");
    printf("Asculta pe portul %d...\n", PORT);

    while (1) {
        // Aloc─âm memorie pentru cererea curent─â (pentru a o pasa ├«n siguran╚¢─â thread-ului)
        client_request_t *req = malloc(sizeof(client_request_t));
        req->sockfd = sockfd;
        req->addr_len = sizeof(req->client_addr);

        int n = recvfrom(sockfd, req->buffer, BUFFER_SIZE - 1, 0, 
                         (struct sockaddr *)&(req->client_addr), &(req->addr_len));
        if (n < 0) {
            free(req);
            continue;
        }
        req->buffer[n] = '\0'; // Terminator de ╚Öir ├«n C

        // Cre─âm un thread nou pentru procesarea pachetului (Concuren╚¢─â)
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, proceseaza_cerere, (void*)req) == 0) {
            pthread_detach(thread_id); // Thread-ul ├«╚Öi elibereaz─â singur resursele la final
        } else {
            perror("Eroare la crearea thread-ului");
            free(req);
        }
    }

    close(sockfd);
    return 0;
}
