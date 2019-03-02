#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../includes/linkedlist.h"

char *int_str(void *x){
    switch (*(int*)x) {
        case 2:
            return "2";
        case 3:
            return "3";
        default:
            return "INF";
    }
}

int cmp_int(void *x, void *y){
    return (*(int *) x - *(int *)y);
}

int main(){
    llist *l = llist_new();
    int a = 3;
    int b = 2;
    llist_add(l, &a);
    llist_add(l, &b);
    llist_add(l, &b);
    llist_add(l, &a);
    llist_add(l, &b);
    llist_print(stdout, l, int_str);
    while(llist_pop(l)){
        llist_print(stdout, l, int_str);
    }
    llist_add(l, &b);
    llist_add(l, &b);
    llist_add(l, &a);
    llist_add(l, &b);
    llist_print(stdout, l, int_str);
    llist_del(l, &a, cmp_int);
    llist_print(stdout, l, int_str);
    llist_destroy(l);
    llist_free(l);
    return 0;
}
