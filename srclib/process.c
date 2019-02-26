#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>

#include "../includes/picohttpparser.h"
#include "../includes/process.h"

#define MAXBUF 4096
#define MAXHEADERS 100
#define MAXTIME 100
#define MAXMETHOD 10
#define MAXSIZE 5
#define MAXMETH 15
#define MAXPATH 4096
#define MAXFILE 4096
#define MAXRES 4096
#define MAXEXT 10
#define MAXTYPE 50
#define MAXAUX 4096
#define MAXRESPONSE 999999999

/* CONFIG FILE*/
#define ABSDIR "/mnt/c/Users/Sergamar/Desktop/Uni/RedesII/www"
#define SVRNAME "MyServer"

int get_response(char* path, struct phr_header* headers, size_t num_headers, char** response);
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
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH], res[MAXRES];
    char response[MAXRESPONSE];
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
    get_response(path, headers, num_headers, &response);
    printf("%s", response);
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

int gmt_time_http(char** res, int tam){
    time_t act = time(0);
    struct tm tm = *gmtime(&act);
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}

int general_headers(char** res){
    char aux[MAXAUX];
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
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}

int get_type(char* ext, char** res){
    if(strcmp(ext, ".txt")){
        strcpy(*res, "text/plain");
        return 1;
    }
    if(strcmp(ext, ".html") || strcmp(ext, ".htm")){
        strcpy(*res, "text/html");
        return 1;
    }
    if(strcmp(ext, ".gif")){
        strcpy(*res, "image/gif");
        return 1;
    }
    if(strcmp(ext, ".jpg") || strcmp(ext, ".jpeg")){
        strcpy(*res, "image/jpeg");
        return 1;
    }
    if(strcmp(ext, ".mpg") || strcmp(ext, ".mpeg")){
        strcpy(*res, "image/mpeg");
        return 1;
    }
    if(strcmp(ext, ".doc") || strcmp(ext, ".docx")){
        strcpy(*res, "application/msword");
        return 1;
    }
    if(strcmp(ext, ".pdf")){
        strcpy(*res, "application/pdf");
        return 1;
    }
    return 0;
}

int get_response(char* path, struct phr_header* headers, size_t num_headers, char** response){
    FILE* fp;
    int size;
    char buf[MAXBUF], abspath[MAXPATH], content[MAXFILE], sizestr[MAXSIZE], ext[MAXEXT];
    char type[MAXTYPE], aux[MAXAUX];
    strcat(abspath, ABSDIR);
    strcat(abspath, path);
    if(!get_type(ext, &type)){
        /*return not_implemented_response()*/
    }
    fp = fopen(abspath, "r");
    if(!fp){
        /*return not_found_response()*/
    }
    size = fread(content, 1 ,sizeof(content), fp);
    strcat(response, "HTTP/1.1 200 OK\r\n");
    /*HEADERS*/
    general_headers(&aux);
    strcat(*response, aux);
    strcat(*response, "Last-Modified: ");
    last_modified_http(abspath, &aux, MAXAUX);
    strcat(*response, aux);
    strcat(*response, "\r\n");
    sprintf(sizestr, "%d", size);
    strcat(*response, "Content-Length: ");
    strcat(*response, sizestr);
    strcat(*response, "\r\n");
    strcat(*response, "Content-Type: ");
    strcat(*response, type);
    strcat(*response, "\r\n\r\n");
    /*BODY*/
    strcat(*response, content);
    return 1;
}
