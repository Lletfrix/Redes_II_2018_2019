#include <pthread.h>
#include <stdlib.h>
#include "../includes/thrpool.h"

int __thread_init(int i, thr *recipent){
    if(recipent){
        //(*recipent).tid = i;
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
        }
        free(pool);
    }
}

int thrpool_resize(struct thrpool *pool){
    //TODO;
    return 0;
}

int thrpool_execute(struct thrpool *pool, const unsigned int initial){
    if(!pool){
        return 0;
    }
    unsigned int limit = initial < pool->max ? initial : pool->max;
    for (unsigned int i = 0; i < limit; ++i){
        pthread_create(&pool->threads[i].tid, NULL, pool->thread_routine, (void *) i);
        pool->threads[i].st=FREE;
        pthread_detach(pool->threads[i].tid);
    }
    return 1;
}
