#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

#include "../includes/picohttpparser.h"
#include "../includes/process.h"

#define MAXBUF 4096
#define MAXHEADERS 100
#define MAXMETHOD 10
#define MAXMETH 15
#define MAXPATH 4096
#define MAXFILE 4096
#define MAXRES 4096
#define MAXEXT 10
#define ABSDIR "/home/alumnos/e356632/content/www"

char* get_response(char* path, struct phr_header* headers, size_t num_headers);
char* post_response(char* path, struct phr_header* headers, size_t num_headers);
char* options_response(char* path, struct phr_header* headers, size_t num_headers);
char* bad_request_response();
char* not_found_response();

int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH], file[MAXFILE], res[MAXRES];
    struct phr_header headers[MAXHEADERS];
    len = recv(clientfd, buf, MAXBUF, 0);
    printf("%s\n", buf);
    num_headers = sizeof(headers) / sizeof(headers[0]);
    pret = phr_parse_request(buf, len, &method, &method_len, &path, &path_len,
                            &minor_version, headers, &num_headers, prevbuflen);
    if(pret < 0){
        /*res = bad_request_response()*/
    }

    sprintf(method_aux, "%.*s", (int)method_len, method);
    sprintf(path_aux, "%.*s", (int)path_len, path);
    /*sprintf(ext, "%s", strrchr(path_aux, '.'));*/

    /*if(!strcmp(method_aux, "GET")){
        res = get_response(path, headers, num_headers);
    }
    else if(!strcmp(method_aux, "POST")){
        res = post_response(path, headers, num_headers);
    }
    else if(!strcmp(method_aux, "OPTIONS")){
        res = options_response(path, headers, num_headers);
    }
    else{

    }*/
    /*Just for testing purposes*/
    /*printf("request is %d bytes long\n", pret);
    printf("method is %.*s\n", (int)method_len, method);
    printf("path is %.*s\n", (int)path_len, path);
    printf("HTTP version is 1.%d\n", minor_version);
    printf("headers:\n");
    for (i = 0; i != num_headers; ++i) {
        printf("%.*s: %.*s\n", (int)headers[i].name_len, headers[i].name,
              (int)headers[i].value_len, headers[i].value);
    }
    printf("%s\n", buf+pret);*/
    return 0;
}

char* get_response(char* path, struct phr_header* headers, size_t num_headers){
    FILE* fp;
    fp = fopen(path, "r");
    if(!fp){
        /*return not_found_response()*/
    }
}
