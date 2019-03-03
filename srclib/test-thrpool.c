#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <syslog.h>
#include <pthread.h>
#include "../includes/linkedlist.h"
#include "../includes/thrpool.h"


void *thread_test(void *arg){
    struct pthread_args args;
    args = *(struct pthread_args *)arg;
    printf("Soy el hilo %d\n", args.index);
    free(arg);
    return NULL;
}

void *thread_process(void *arg){
    struct pthread_args args;
    pthread_cleanup_push(free, arg);
    args = *(struct pthread_args *)arg;
    llist_add(args.pool->busy, &args.pool->threads[args.index].tid);
    printf("Soy el hilo de TID: %ld y he entrado en lan lista de busy\n", args.pool->threads[args.index].tid);
    sleep(30);
    pthread_cleanup_pop(1);
    return NULL;
}

int main(){
    struct thrpool *p = thrpool_new(10, thread_process);
    thrpool_execute(p, 2);
    sleep(5);
    thrpool_terminate(p);
    thrpool_free(p);
    return 0;
}
