#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include "../includes/linkedlist.h"
#include "../includes/thrpool.h"

int __thread_init(int i, thr *recipent){
    if(recipent){
        (*recipent).st = DEAD;
        return 1;
    }
    return 0;
}

struct thrpool *thrpool_new(const unsigned int max, void * (*thr_routine) (void *)){
    struct thrpool *pool = calloc(1, sizeof(struct thrpool));
    if(pool){
        pool->threads = calloc(max, sizeof(thr));
        if(pool->threads){
            pool->max = max;
            pool->thread_routine = thr_routine;
            for (unsigned int i = 0; i < max; ++i){
                __thread_init(i, pool->threads+i);
            }
            pool->free = llist_new();
            pool->busy = llist_new();
            return pool;
        }
        free(pool);
    }
    return NULL;
}

void thrpool_free(struct thrpool* pool){
    if(pool){
        if(pool->threads){
            free(pool->threads);
            llist_destroy(pool->free);
            llist_free(pool->free);
            llist_destroy(pool->busy);
            llist_free(pool->busy);
        }
        free(pool);
    }
}

int thrpool_resize(struct thrpool *pool){
    //TODO
    return 0;
}

int thrpool_execute(struct thrpool *pool, const unsigned int initial){
    if(!pool){
        return 0;
    }
    struct pthread_args *arg;
    unsigned int limit = initial < pool->max ? initial : pool->max;
    for (unsigned int i = 0; i < limit; ++i){
        arg = calloc(1, sizeof(struct pthread_args));
        arg->index = i;
        arg->pool = pool;
        pthread_create(&pool->threads[i].tid, NULL, pool->thread_routine, (void *) arg);
        llist_add(pool->free, &pool->threads[i].tid);
        pool->threads[i].st=FREE;
        pool->n_free += 1;
        pool->n_alive += 1;
        pthread_detach(pool->threads[i].tid);
    }
    return 1;
}

int thrpool_terminate(struct thrpool *pool){
    pthread_t *tid;
    if(pool){
        while((tid = llist_pop(pool->free))){
            pthread_cancel(*tid);
        }
        while((tid = llist_pop(pool->busy))){
            pthread_cancel(*tid);
        }
        return 1;
    }
    return 0;
}
