#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <syslog.h>
#include <pthread.h>
#include <math.h>
#include "../includes/linkedlist.h"
#include "../includes/thrpool.h"

char *tid_string(void *x){
    size_t digits = ceil(log10(* (pthread_t*) x));
    char *s = calloc(digits+1, sizeof(pthread_t));
    snprintf(s, digits+1, "%lu", *(pthread_t *)x);
    return s;
}

int tid_cmp(void *t1, void *t2){
    if(!t1 || !t2) return -1;
    pthread_t *tid1, *tid2;
    tid1 = t1;
    tid2 = t2;
    return *tid1-*tid2;
}

void clean(void *arg){
    struct thrpool *pool = arg;
    pthread_mutex_unlock(&pool->freemtx);
    pthread_mutex_unlock(&pool->busymtx);
}

void *thread_process(void *arg){
    struct thrpool *pool = arg;
    void *aux;
    pthread_t tid = pthread_self();
    pthread_cleanup_push(clean, arg);

    pthread_mutex_lock(&pool->freemtx);
    aux = llist_del(pool->free, &tid, tid_cmp);
    if(aux) free(aux);
    printf("He salido de Free: ");
    llist_print(stdout, pool->free, tid_string);
    pthread_mutex_unlock(&pool->freemtx);

    pthread_mutex_lock(&pool->busymtx);
    llist_add(pool->busy, &tid);
    printf("Soy el hilo de TID: %lu y he entrado en lan lista de busy\n", tid);
    pthread_mutex_unlock(&pool->busymtx);

    sleep(10);
    pthread_cleanup_pop(1);
    return NULL;
}

int main(){
    struct thrpool *p = thrpool_new(10, thread_process);
    thrpool_execute(p, 3);
    sleep(5);
    printf("Free: ");
    llist_print(stdout, p->free, tid_string);
    printf("\nBusy: " );
    llist_print(stdout, p->busy, tid_string);
    printf("\n");
    thrpool_terminate(p);
    thrpool_free(p);
    return 0;
}
