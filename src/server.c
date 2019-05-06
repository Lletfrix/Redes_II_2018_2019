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
#include "../includes/daemon.h"

#define MAXTHR 15

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
    pthread_exit(NULL);
}

void *func(void *args){
    int clientfd;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(struct sockaddr_in);
    while(1){
        pthread_mutex_lock(&mutex_accept);
        clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
        pthread_mutex_unlock(&mutex_accept);
        process_http(clientfd);
        if(clientfd >= 0)
            close_connection(clientfd);
    }
    return NULL;
}

int main(int argc, char **argv){
    char ip[] = "127.0.0.1";
    int port = 5001;

    demonizar(argv[0]);

    pool = thrpool_new(MAXTHR, func);

    sockfd = tcp_listen(ip, port);

    signal(SIGINT, handle_sigint);
    signal(SIGUSR1, handle_sigusr1);

    thrpool_execute(pool, MAXTHR);
    for(;;) pause();
    return 0;
}
