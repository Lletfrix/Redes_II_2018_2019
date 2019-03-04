#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>

#include "../includes/connections.h"
#include "../includes/process.h"
#include "../includes/thrpool.h"

#define MAXTHR 4

int sockfd;
struct thrpool* pool;

pthread_mutex_t mutex_accept = PTHREAD_MUTEX_INITIALIZER;

void handle_sigint(int sig)
{
    close_connection(sockfd);
    thrpool_terminate(pool);
    thrpool_free(pool);
    //close_connection(clientfd);
    exit(EXIT_SUCCESS);
}

void *func(void *args){
    int clientfd;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(struct sockaddr_in);
    while(1){
        pthread_mutex_lock(&mutex_accept);
        clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
        printf("Soy %lu y he aceptado conexion.\n", pthread_self());
        pthread_mutex_unlock(&mutex_accept);
        process_http(clientfd);
        close_connection(clientfd);
    }
}

int main(void){
    char ip[] = "127.0.0.1";
    int port = 5001;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(client);

    pool = thrpool_new(4, func);

    sockfd = tcp_listen(ip, port);
    printf("Estamos escuchando\n");

    signal(SIGINT, handle_sigint);

    thrpool_execute(pool, 4);
    for(;;) pause();
}
