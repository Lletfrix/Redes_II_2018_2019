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
    thrpool_terminate(pool);
    thrpool_free(pool);
    close_connection(sockfd);

    int n_fd = getdtablesize();
    for(int i = 3; i < n_fd; ++i){
        close(i);
    }

    exit(EXIT_SUCCESS);
}

void handle_sigusr1(int sig){
    pthread_mutex_unlock(&mutex_accept);
    pthread_mutex_unlock(&pool->freemtx);
    pthread_mutex_unlock(&pool->busymtx);
    //close(clientfd);
    pthread_exit(NULL);
}

void *func(void *args){
    int clientfd;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(struct sockaddr_in);
    signal(SIGUSR1, handle_sigusr1);
    while(1){
        pthread_mutex_lock(&mutex_accept);
        clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
        printf("\033[48;2;%d;%d;%dm", 255, 0, 0);
        printf("Soy (%lu, %d) y he aceptado conexion.\n", pthread_self(), clientfd);
        pthread_mutex_unlock(&mutex_accept);
        process_http(clientfd);
        printf("\033[48;2;%d;%d;%dm", 0, 255, 0);
        printf("Soy (%lu, %d) y he terminado conexion.\n", pthread_self(), clientfd);
        close_connection(clientfd);
    }
    return NULL;
}

int main(void){
    char ip[] = "127.0.0.1";
    int port = 5001;
    //struct sockaddr_in client;
    //socklen_t addrlen = sizeof(client);

    sockfd = tcp_listen(ip, port);

    if(sockfd < 0) return sockfd;

    pool = thrpool_new(15, func);

    printf("Estamos escuchando\n");

    signal(SIGINT, handle_sigint);

    thrpool_execute(pool, 15);
    for(;;) pause();
    return 0;
}
