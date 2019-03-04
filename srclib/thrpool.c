#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include "../includes/linkedlist.h"
#include "../includes/thrpool.h"

struct thrpool *thrpool_new(const unsigned int max, void * (*thr_routine) (void *)){
    struct thrpool *pool = calloc(1, sizeof(struct thrpool));
    if(pool){ //TODO: Handle llist_new fail
        pool->max = max;
        pool->thread_routine = thr_routine;
        pool->free = llist_new();
        pool->busy = llist_new();
        pthread_mutex_init(&pool->freemtx, NULL);
        pthread_mutex_init(&pool->busymtx, NULL);
        return pool;
    }
    return NULL;
}

void thrpool_free(struct thrpool* pool){
    if(pool){
        pthread_mutex_lock(&pool->freemtx);
        pthread_mutex_lock(&pool->busymtx);
        llist_destroy(pool->free);
        llist_free(pool->free);
        llist_destroy(pool->busy);
        llist_free(pool->busy);
        pthread_mutex_unlock(&pool->freemtx);
        pthread_mutex_unlock(&pool->busymtx);
        free(pool);
    }
}

/*int thrpool_resize(struct thrpool *pool){
    if(pool & pool->need_resz){
        if(pool->need_resz > 0 & n_alive < max){
            unsigned int limit = (max-n_alive) < pool->need_resz ? (max-n_alive) : pool->need_resz;
            for (unsigned int i = 0; i < limit; ++i){

            }
        }
    }
    return 0;
}*/

int thrpool_execute(struct thrpool *pool, const unsigned int initial){
    if(!pool){
        return 0;
    }
    pthread_t *tid;
    unsigned int limit = initial < pool->max ? initial : pool->max;
    for (unsigned int i = 0; i < limit; ++i){
        tid = calloc(1, sizeof(pthread_t));
        pthread_mutex_lock(&pool->freemtx);
        pthread_create(tid, NULL, pool->thread_routine, (void *) pool);
        llist_add(pool->free, tid);
        pthread_mutex_unlock(&pool->freemtx);
        pool->n_free += 1;
        pool->n_alive += 1;
        //pthread_detach(*tid);
    }
    return 1;
}

int thrpool_terminate(struct thrpool *pool){
    pthread_t *tid = NULL;
    if(pool){
        pthread_mutex_lock(&pool->freemtx);
        while((tid = llist_pop(pool->free))){
            pthread_cancel(*tid);
            pthread_join(*tid, NULL);
        }
        pthread_mutex_unlock(&pool->freemtx);

        pthread_mutex_lock(&pool->busymtx);
        while((tid = llist_pop(pool->busy))){
            pthread_cancel(*tid);
            pthread_join(*tid, NULL);
        }
        pthread_mutex_unlock(&pool->busymtx);
        return 1;
    }
    return 0;
}
