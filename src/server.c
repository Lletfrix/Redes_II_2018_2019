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
#include <syslog.h>

#include "../includes/connections.h"
#include "../includes/process.h"
#include "../includes/thrpool.h"
#include "../includes/daemon.h"
#include "../includes/config.h"
#include "../includes/error_handling.h"

#define CONFIG_PATH "/server.conf"

int sockfd;
struct thrpool* pool;

pthread_mutex_t mutex_accept = PTHREAD_MUTEX_INITIALIZER;

void handle_sigint(int sig)
{
    thrpool_terminate(pool);
    thrpool_free(pool);
    close_connection(sockfd);
    closelog();

    int n_fd = getdtablesize();
    for(int i = 3; i < n_fd; ++i){
        close(i);
    }
    config_destroy();
    //config_destroy(); TODO: fix this
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
        syslog(LOG_INFO, "Hilo %lu: Voy a aceptar una conexión.", pthread_self());
        clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
        pthread_mutex_unlock(&mutex_accept);
        syslog(LOG_INFO, "Hilo %lu: Voy a procesar una petición.", pthread_self());
        process_http(clientfd);
        if(clientfd >= 0)
        syslog(LOG_INFO, "Hilo %lu: Voy a cerrar una conexión.", pthread_self());
        close_connection(clientfd);
    }
    return NULL;
}

int main(int argc, char **argv){
    char cwd[PATHMAX];
    char config_path[PATHMAX];
    char ip[] = "127.0.0.1";
    int port = 5001;
    demonizar(argv[0], cwd);
    strcpy(config_path, cwd);
    strcat(config_path, CONFIG_PATH);
    if (UINT_ERROR == load_config_from_file(config_path)){
        syslog(LOG_DEBUG, "%s - Archivo con ruta: %s", "No se ha podido cargar el diccionario de configuración del servidor.", config_path);
        exit(0);
    }
    config_set("cwd", cwd);
    syslog(LOG_INFO, "%s", "Creando pool de hilos.");
    pool = thrpool_new(config_get_int("max_clients"), func);
    port = config_get_int("listening_port");
    syslog(LOG_INFO, "%s%s%s%d.", "Escuchando en la ip: ", ip, " con puerto ", port);
    sockfd = tcp_listen(ip, port);

    signal(SIGINT, handle_sigint);
    signal(SIGUSR1, handle_sigusr1);

    syslog(LOG_INFO, "%s", "Lanzando pool de hilos.");
    thrpool_execute(pool, config_get_int("max_clients"));
    for(;;) pause();
    return 0;
}
