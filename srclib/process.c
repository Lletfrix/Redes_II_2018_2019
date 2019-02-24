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

/* CONFIG FILE*/
#define ABSDIR "/mnt/c/Users/Sergamar/Desktop/Uni/RedesII/www"
#define SVRNAME "MyServer"

char* get_response(char* path, struct phr_header* headers, size_t num_headers);
char* post_response(char* path, struct phr_header* headers, size_t num_headers);
char* options_response(char* path, struct phr_header* headers, size_t num_headers);
char* bad_request_response();
char* not_found_response();
char* gmt_time_http();
char* general_headers();
char* last_modified_http(char* path);

int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH], res[MAXRES];
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

char* gmt_time_http(){
    char buf[MAXTIME];
    time_t act = time(0);
    struct tm tm = *gmtime(&act);
    strftime(buf, sizeof(buf), "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return buf;
}

char* general_headers(){
    char buf[MAXBUF];
    strcat(buf, "Date: ");
    strcat(buf, gmt_time_http());
    strcat(buf, "\r\n");
    strcat(buf, "Server: ");
    strcat(buf, SVRNAME);
    strcat(buf, "\r\n");
    return buf;
}

char* last_modified_http(char* path){
    char buf[MAXTIME];
    struct tm tm;
    struct stat atrib;
    stat(path, &atrib);
    tm = *gmtime(&(atrib.st_mtime));
    strftime(buf, sizeof(buf), "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return buf;
}

char* get_type(char* ext){
    char type[MAXTYPE];
    if(strcmp(ext, ".txt")){
        strcpy(type, "text/plain");
    }
    if(strcmp(ext, ".html") || strcmp(ext, ".htm")){
        strcpy(type, "text/html");
    }
    if(strcmp(ext, ".gif")){
        strcpy(type, "image/gif");
    }
    if(strcmp(ext, ".jpg") || strcmp(ext, ".jpeg")){
        strcpy(type, "image/jpeg");
    }
    if(strcmp(ext, ".mpg") || strcmp(ext, ".mpeg")){
        strcpy(type, "image/mpeg");
    }
    if(strcmp(ext, ".doc") || strcmp(ext, ".docx")){
        strcpy(type, "application/msword");
    }
    if(strcmp(ext, ".pdf")){
        strcpy(type, "application/pdf");
    }
    else{
        type = NULL;
    }
    return type;
}

char* get_response(char* path, struct phr_header* headers, size_t num_headers){
    FILE* fp;
    char* response;
    int size;
    char buf[MAXBUF], abspath[MAXPATH], content[MAXFILE], sizestr[MAXSIZE], ext[MAXEXT];
    char type[MAXTYPE];
    strcat(abspath, ABSDIR);
    strcat(abspath, path);
    type = get_type(ext);
    if(!type){
        /*return not_implemented_response()*/
    }
    fp = fopen(abspath, "r");
    if(!fp){
        /*return not_found_response()*/
    }
    size = read(fp, content, MAXFILE);
    strcat(response, "HTTP/1.1 200 OK\r\n");
    /*HEADERS*/
    strcat(response, general_headers());
    strcat(response, "Last-Modified: ");
    strcat(response, last_modified_http(abspath));
    strcat(response, "\r\n");
    sprintf(sizestr, "%d", size);
    strcat(response, "Content-Length: ");
    strcat(response, sizestr);
    strcat(response, "\r\n");
    strcat(response, "Content-Type: ");
    strcat(response, type);
    strcat(response, "\r\n\r\n");
    /*BODY*/
    strcat(response, content);
    return response;
}
