#include <pthread.h>
#include "thrpool.h"

thr * __thread_new(int i){
    thr *new = calloc(1, sizeof(thr));
    if(new){
        new->tid = i;
        new->thr_status = DEAD;
    }
    return new;
}

void __thread_free(thr *thr){
    if(thr)
        free(thr);
}


struct thrpool *thrpool_create(const unsigned int max, (void *) *thr_routine (void *)){
    struct thrpool *pool = calloc(1, sizeof(struct thrpool));
    if(pool){
        pool->threads = calloc(max, sizeof(thr));
        if(pool->threads){
            pool->max = max;
            pool->thread_routine = thr_routine;
            for (unsigned int i = 0; i < max; ++i){
                *(threads + i) = __thread_new(i);
            }
            return pool;
        }
        free(pool);
    }
    return NULL;
};

void thrpool_free(struct thrpool* pool){
    if(pool){
        if(pool->threads){
            for (unsigned int i = 0; i < max ; ++i){
                __thread_free(threads+i);
            }
            free(pool->threads);
        }
        free(pool);
    }
}

int thrpool_resize(struct thrpool *pool){
    //TODO;
};

int thrpool_execute(struct thrpool *pool, const unsigned int initial){
    if(!pool){
        return -1;
    }
    unsigned int limit =
    for (unsigned int i = 0; i < initial; ++i){
        pthread_create(pool->threads[i]->tid, NULL, pool->thread_routine, (void *) pool->threads[i]->tid);
        pool->threads[i]->st=FREE;
    }
}
