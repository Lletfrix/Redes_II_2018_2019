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
#define CHUNK 4096

/* CONFIG FILE*/
#define ABSDIR "/mnt/c/Users/Sergamar/Desktop/Uni/RedesII/www"
#define SVRNAME "MyServer"

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int post_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int options_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int bad_request_response(int clientfd);
int method_not_allowed_response(int clientfd);
int not_found_response(int clientfd);
int gmt_time_http(char** res, int tam);
int general_headers(char** res);
int last_modified_http(char* path, char** res, int tam);
int get_type(char* ext, char** res);

int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH];
    struct phr_header headers[MAXHEADERS];
    bzero(buf, MAXBUF);
    len = recv(clientfd, buf, MAXBUF, 0);
    if(len <= 0){
        return EXIT_SUCCESS;
    }
    num_headers = sizeof(headers) / sizeof(headers[0]);
    pret = phr_parse_request(buf, len, &method, &method_len, &path, &path_len,
                            &minor_version, headers, &num_headers, prevbuflen);
    if(pret < 0){
        return bad_request_response(clientfd);
    }
    sprintf(method_aux, "%.*s", (int)method_len, method);
    sprintf(path_aux, "%.*s", (int)path_len, path);
    if(!strcmp(method_aux, "GET")){
        return get_handler(path_aux, headers, num_headers, clientfd);
    }/*
    else if(!strcmp(method_aux, "POST")){
        return post_handler(path_aux, headers, num_headers, clientfd);
    }
    else if(!strcmp(method_aux, "OPTIONS")){
        return options_handler(path_aux, headers, num_headers, clientfd);
    }*/
    return method_not_allowed_response(clientfd);
}

int get_size(char* path){
    struct stat atrib;
    stat(path, &atrib);
    return atrib.st_size;
}

int gmt_time_http(char** res, int tam){
    char timeaux[MAXTIME];
    time_t act = time(0);
    struct tm tm = *gmtime(&act);
    strftime(timeaux, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    strcat(*res, timeaux);
    return 1;
}

int general_headers(char** res){
    strcat(*res, "Date: ");
    gmt_time_http(res, MAXAUX);
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
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}

int get_type(char* ext, char** res){
    if(!strcmp(ext, ".txt")){
        strcpy(*res, "text/plain");
        return 1;
    }
    if(!strcmp(ext, ".html") || !strcmp(ext, ".htm")){
        strcpy(*res, "text/html");
        return 1;
    }
    if(!strcmp(ext, ".gif")){
        strcpy(*res, "image/gif");
        return 1;
    }
    if(!strcmp(ext, ".jpg") || !strcmp(ext, ".jpeg")){
        strcpy(*res, "image/jpeg");
        return 1;
    }
    if(!strcmp(ext, ".mpg") || !strcmp(ext, ".mpeg")){
        strcpy(*res, "image/mpeg");
        return 1;
    }
    if(!strcmp(ext, ".doc") || !strcmp(ext, ".docx")){
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
    int size;
    char abspath[MAXPATH], sizestr[MAXSIZE];
    char* ext;
    char* response;
    char* type;
    char* aux;
    int filefd;
    off_t offset = 0;
    aux = calloc(MAXAUX, sizeof(char));
    if(!aux){
        return EXIT_FAILURE;
    }
    response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        free(aux);
        return EXIT_FAILURE;
    }
    type = calloc(MAXTYPE, sizeof(char));
    if(!type){
        free(aux);
        free(response);
        return EXIT_FAILURE;
    }
    bzero(abspath, MAXPATH);
    strcat(abspath, ABSDIR);
    if(!strcmp(path, "/")){
        strcat(path, "index.html");
    }
    strcat(abspath, path);
    ext = strrchr(path, '.');
    if(!get_type(ext, &type)){
        not_found_response(clientfd);
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    filefd = open(abspath, O_RDONLY);
    if(filefd < 0){
        not_found_response(clientfd);
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    size = get_size(abspath);
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
    send(clientfd, response, strlen(response), 0);
    while(offset < size){
        sendfile(clientfd, filefd, &offset, CHUNK);
    }
    free(aux);
    free(response);
    free(type);
    close(filefd);
    return EXIT_SUCCESS;
}

int not_found_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 404 Not Found\r\n");
    general_headers(&response);
    send(clientfd, response, strlen(response), 0);
    free(response);
    return EXIT_SUCCESS;
}

int method_not_allowed_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 405 Method Not Allowed\r\n");
    general_headers(&response);
    send(clientfd, response, strlen(response), 0);
    free(response);
    return EXIT_SUCCESS;
}

int bad_request_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 400 Bad Request\r\n");
    general_headers(&response);
    send(clientfd, response, strlen(response), 0);
    free(response);
    return EXIT_SUCCESS;
}
