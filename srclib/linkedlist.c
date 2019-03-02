#include <stdlib.h>
#include "../includes/linkedlist.h"

struct lnode *__lnode_new(void *val);

void __lnode_free();

llist *llist_new(){
    llist *l = calloc(1, sizeof(llist));
    return l;
};

void llist_free(llist *l){
    if(l) free(l);
};

void llist_destroy(llist *l){
    struct lnode *aux;
    struct lnode *first;
    if(l){
        first = l->first;
            while(first){
                aux = first->next;
                __lnode_free(first);
                first = aux;
            }
        l->first = NULL;
    }
}

void *llist_head(llist *l){
    if(l)
        return l->first->val;
    return NULL;
};

int llist_add(llist *l, void *elem){
    if(l){
        struct lnode *new = __lnode_new(elem);
        new->next=l->first;
        l->first = new;
        return 1;
    }
    return 0;
}

int llist_del(llist *l, void *elem, int (*cmp_func) (void *, void *)){
    if(l){
        struct lnode *curr = NULL, *next = l->first;
        if (!cmp_func(next->val, elem)){
            __lnode_free(next);
            l->first = NULL;
            return 1;
        }
        curr = l->first; next = curr->next;
        while(next){
            if (!cmp_func(next->val, elem)){
                curr->next = next->next;
                __lnode_free(next);
                return 1;
            }
        }
    }
    return 0;
}

void *llist_pop(llist *l){
    if(l && l->first){
        void *aux = l->first->val;
        struct lnode *to_pop = l->first;
        l->first = l->first->next;
        __lnode_free(to_pop);
        return aux;
    }
    return NULL;
}


struct lnode *__lnode_new(void *val){
    struct lnode *new = calloc(1, sizeof(struct lnode));
    new->val = val;
    return new;
}

void __lnode_free(struct lnode *ln){
    free(ln);
}
