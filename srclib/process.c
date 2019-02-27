#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/sendfile.h>

#include "../includes/picohttpparser.h"
#include "../includes/process.h"

#define MAXBUF 4096
#define MAXHEADERS 100
#define MAXTIME 100
#define MAXMETHOD 10
#define MAXSIZE 5
#define MAXMETH 15
#define MAXPATH 4096
#define MAXFILE 99999
#define MAXRES 4096
#define MAXEXT 10
#define MAXTYPE 50
#define MAXAUX 4096
#define MAXRESPONSE 999
#define CHUNK 1024

/* CONFIG FILE*/
#define ABSDIR "/home/alumnos/e356632/RedesII/www"
#define SVRNAME "MyServer"

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
char* post_response(char* path, struct phr_header* headers, size_t num_headers);
char* options_response(char* path, struct phr_header* headers, size_t num_headers);
char* bad_request_response();
char* not_found_response();
int gmt_time_http(char** res, int tam);
int general_headers(char** res);
int last_modified_http(char* path, char** res, int tam);
int get_type(char* ext, char** res);

int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH];
    //char* response;
    //int size;
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
    get_handler(path_aux, headers, num_headers, clientfd); //Testing
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
    //send(clientfd, response, size, 0);
    return 0;
}

int get_size(char* path){
    struct stat atrib;
    stat(path, &atrib);
    return atrib.st_size;
}

int gmt_time_http(char** res, int tam){
    time_t act = time(0);
    struct tm tm = *gmtime(&act);
    *res = calloc(MAXTIME, sizeof(char));
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}

int general_headers(char** res){
    char* aux;
    *res = calloc(MAXHEADERS, sizeof(char));//TODO
    strcat(*res, "Date: ");
    gmt_time_http(&aux, MAXAUX);
    strcat(*res, aux);
    strcat(*res, "\r\n");
    strcat(*res, "Server: ");
    strcat(*res, SVRNAME);
    strcat(*res, "\r\n");
    return 1;
}

int last_modified_http(char* path, char** res, int tam){
    struct tm tm;
    struct stat atrib;
    stat(path, &atrib);
    tm = *gmtime(&(atrib.st_mtime));
    *res = calloc(MAXTIME, sizeof(char));//TODO
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}

int get_type(char* ext, char** res){
    *res = calloc(MAXTYPE, sizeof(char));//TODO
    if(!strcmp(ext, ".txt")){
        strcpy(*res, "text/plain");
        return 1;
    }
    if(!strcmp(ext, ".html") || strcmp(ext, ".htm")){
        strcpy(*res, "text/html");
        return 1;
    }
    if(!strcmp(ext, ".gif")){
        strcpy(*res, "image/gif");
        return 1;
    }
    if(!strcmp(ext, ".jpg") || strcmp(ext, ".jpeg")){
        strcpy(*res, "image/jpeg");
        return 1;
    }
    if(!strcmp(ext, ".mpg") || strcmp(ext, ".mpeg")){
        strcpy(*res, "image/mpeg");
        return 1;
    }
    if(!strcmp(ext, ".doc") || strcmp(ext, ".docx")){
        strcpy(*res, "application/msword");
        return 1;
    }
    if(!strcmp(ext, ".pdf")){
        strcpy(*res, "application/pdf");
        return 1;
    }
    return 0;
}

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd){
    //FILE* fp;
    int size;
    char abspath[MAXPATH], sizestr[MAXSIZE];
    char* ext;
    char* response;
    //char* content;
    char* type;
    char* aux;
    int filefd;
    off_t offset = 0;
    bzero(abspath, MAXPATH);
    strcat(abspath, ABSDIR);
    printf("\n%s\n", path);
    if(!strcmp(path, "/")){
        strcat(path, "index.html");
    }
    strcat(abspath, path);
    ext = strrchr(path, '.');
    if(!get_type(ext, &type)){
        /*return not_implemented_response()*/
    }
    /*fp = fopen(abspath, "rb");
    if(!fp){
        return not_found_response()
        printf("No he abierto el fichero");
    }*/
    response = calloc(MAXRESPONSE, sizeof(char));//TODO
    /*content = calloc(MAXFILE, sizeof(char));
    size = fread(content, 1 ,MAXFILE, fp);*/

    filefd = open(abspath, O_RDONLY);
    if(filefd < 0){
        //return not_found_response()
    }
    size = get_size(abspath);
    printf("%s\n", abspath);
    strcat(response, "HTTP/1.1 200 OK\r\n");
    /*HEADERS*/
    general_headers(&aux);
    strcat(response, aux);
    strcat(response, "Last-Modified: ");
    last_modified_http(abspath, &aux, MAXAUX);
    strcat(response, aux);
    strcat(response, "\r\n");
    sprintf(sizestr, "%d", size);
    strcat(response, "Content-Length: ");
    strcat(response, sizestr);
    strcat(response, "\r\n");
    strcat(response, "Content-Type: ");
    strcat(response, type);
    strcat(response, "\r\n\r\n");
    /*BODY*/
    //strcat(*response, content);
    send(clientfd, response, strlen(response), 0);
    while(offset < size){
        printf("\n Enviando %s\n", abspath);
        sendfile(clientfd, filefd, &offset, CHUNK);
    }
    return 1;
}
