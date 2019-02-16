#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

#include "../includes/picohttpparser.h"
#include "../includes/process.h"

#define MAXBUF 4096
#define MAXHEADERS 100
#define MAXMETHOD 10
#define MAXPATH 100
int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version, i;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF];
    struct phr_header headers[MAXHEADERS];
    len = recv(clientfd, buf, MAXBUF, 0);
    printf("%s\n", buf);
    num_headers = sizeof(headers) / sizeof(headers[0]);
    pret = phr_parse_request(buf, len, &method, &method_len, &path, &path_len,
                            &minor_version, headers, &num_headers, prevbuflen);
    if(pret == -1){
        return ParseError;
    }
    if(pret == -2){
        return RequestIsTooLongError;
    }
    /*Just for testing purposes*/
    printf("request is %d bytes long\n", pret);
    printf("method is %.*s\n", (int)method_len, method);
    printf("path is %.*s\n", (int)path_len, path);
    printf("HTTP version is 1.%d\n", minor_version);
    printf("headers:\n");
    for (i = 0; i != num_headers; ++i) {
        printf("%.*s: %.*s\n", (int)headers[i].name_len, headers[i].name,
              (int)headers[i].value_len, headers[i].value);
    }
    printf("%s\n", buf+pret);
    return 0;
}
