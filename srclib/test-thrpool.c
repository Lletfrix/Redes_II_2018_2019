#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <syslog.h>
#include <pthread.h>
#include "../includes/thrpool.h"


void *thread_test(void *arg){
    printf("Soy el hilo %d\n", (int) arg);
    return NULL;
}

int main(){
    struct thrpool *p = thrpool_new(10, thread_test);
    thrpool_execute(p, 2);
    sleep(5);
    thrpool_free(p);
    return 0;
}
