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
#include <pthread.h>
#include "../includes/picohttpparser.h"
#include "../includes/process.h"

#define MAXBUF 4096
#define MAXHEADERS 100
#define MAXTIME 100
#define MAXMETHOD 10
#define MAXSIZE 5
#define MAXLEN 20
#define MAXMETH 15
#define MAXPATH 4096
#define MAXFILE 999999
#define MAXRES 4096
#define MAXEXT 10
#define MAXTYPE 50
#define MAXAUX 4096
#define MAXRESPONSE 999
#define CHUNK 4096
#define MAXSCRIPT 10
#define MAXCOMMAND 500
#define MAXVALUE 200
#define MAXRESULT 1000
#define MAXBODY 99999

/* CONFIG FILE*/
#define ABSDIR "/home/lletfrix/server/www"
#define DIR404 "/home/lletfrix/server/www/404.html"
#define SCRTXT "/home/lletfrix/server/scripts/aux.txt"
#define SVRNAME "MyServer"

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int post_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd, char* body);
int options_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int bad_request_response(int clientfd);
int method_not_implemented_response(int clientfd);
int not_found_response(int clientfd);
int gmt_time_http(char** res, int tam);
int general_headers(char** res);
int last_modified_http(char* path, char** res, int tam);
int get_type(const char* ext, char* res);
int __file_exists(char* abspath);
int run_script(char* abspath, char* body, char* result);
int check_connection(struct phr_header* headers, int num_headers);
int send_script_res(char* res, int clientfd);
int __check_ext(const char *check, const char *ext);

int process_http(int clientfd){
    const char *method, *path;
    int len, pret, minor_version;
    size_t prevbuflen = 0, method_len, path_len, num_headers;
    char buf[MAXBUF], method_aux[MAXMETH], path_aux[MAXPATH], body[MAXBODY];
    struct phr_header headers[MAXHEADERS];
    short keep_alive=1;
    int errcode;
    while(keep_alive){

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
        if(check_connection(headers, num_headers)){
            keep_alive=0;
        }
        sprintf(method_aux, "%.*s", (int)method_len, method);
        sprintf(path_aux, "%.*s", (int)path_len, path);

        //DEBUG

        printf("\033[48;2;%d;%d;%dm", 0, 0, 255);
        printf("\n\nSoy %ld\n", pthread_self());
        printf("request is %d bytes long\n", pret);
        printf("method is %.*s\n", (int)method_len, method);
        printf("path is %.*s\n", (int)path_len, path);
        printf("HTTP version is 1.%d\n", minor_version);
        printf("headers:\n");
        for (int i = 0; i != num_headers; ++i) {
            printf("%.*s: %.*s\n", (int)headers[i].name_len, headers[i].name,
                   (int)headers[i].value_len, headers[i].value);
        }
        //END DEBUG
        if(!strcmp(method_aux, "GET")){
            errcode = get_handler(path_aux, headers, num_headers, clientfd);
        }
        else if(!strcmp(method_aux, "POST")){
            sprintf(body, "%s", buf+pret);
            errcode = post_handler(path_aux, headers, num_headers, clientfd, body);
        }
        else if(!strcmp(method_aux, "OPTIONS")){
            errcode = options_handler(path_aux, headers, num_headers, clientfd);
        }
        if(errcode) keep_alive = 0;
    }
    return method_not_implemented_response(clientfd);
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

int get_type(const char* ext, char* res){
    if(!strcmp(ext, ".txt")){
        strcpy(res, "text/plain");
        return 1;
    }
    if(!strcmp(ext, ".html") || !strcmp(ext, ".htm")){
        strcpy(res, "text/html");
        return 1;
    }
    if(!strcmp(ext, ".gif")){
        strcpy(res, "image/gif");
        return 1;
    }
    if(!strcmp(ext, ".jpg") || !strcmp(ext, ".jpeg")){
        strcpy(res, "image/jpeg");
        return 1;
    }
    if(!strcmp(ext, ".mpg") || !strcmp(ext, ".mpeg")){
        strcpy(res, "image/mpeg");
        return 1;
    }
    if(!strcmp(ext, ".ico")){
        strcpy(res, "image/vnd.microsoft.icon");
        return 1;
    }
    if(!strcmp(ext, ".doc") || !strcmp(ext, ".docx")){
        strcpy(res, "application/msword");
        return 1;
    }
    if(!strcmp(ext, ".pdf")){
        strcpy(res, "application/pdf");
        return 1;
    }
    return 0;
}

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd){
    int size;
    char abspath[MAXPATH]={0}, sizestr[MAXSIZE], script_ext[MAXSCRIPT];
    char* ext;
    char* response;
    char* result;
    char* type;
    char* aux;
    int filefd;
    off_t offset = 0;
    //Allocates memory
    aux = calloc(MAXAUX, sizeof(char));

    response = calloc(MAXRESPONSE, sizeof(char));

    type = calloc(MAXTYPE, sizeof(char));
    if(!type){
        free(aux);
        free(response);
        return EXIT_FAILURE;
    }
    //Build path with index.html
    strcat(abspath, ABSDIR);
    if(!strcmp(path, "/")){
        strcat(path, "index.html");
    }
    strcat(abspath, path);
    ext = strrchr(path, '.');
    //Gets type of request
    if(!get_type(ext, type) && !strrchr(ext,'?')){
        not_found_response(clientfd);
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    //Launch if script
    if(strrchr(ext, '?')){
        sprintf(script_ext, "%.*s", (int)(strrchr(ext, '?') - ext), ext);
        if(!strcmp(script_ext, ".py") || !strcmp(script_ext, ".php")){
            result = calloc(MAXRESULT, sizeof(char));
            if(!result){
                free(aux);
                free(response);
                free(type);
                return EXIT_FAILURE;
            }
            run_script(abspath, NULL, result);
            send_script_res(result, clientfd);
            free(result);
        }
        else{
            not_found_response(clientfd);
        }
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    //Open file descriptor for resource
    filefd = open(abspath, O_RDONLY);
    if(filefd < 0){
        not_found_response(clientfd);
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    //Builds header
    //TODO: Change this for function __build_get_header(response, );
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
    //Sends header
    send(clientfd, response, strlen(response), 0);
    /*BODY*/
    //Sends chunked body
    while(offset < size){
        sendfile(clientfd, filefd, &offset, CHUNK);
    }
    //Free stuff
    free(aux);
    free(response);
    free(type);
    if(filefd >= 0)
        close(filefd);
    return EXIT_SUCCESS;
}

int options_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd){
    char* response;
    char* aux;
    response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    aux = calloc(MAXAUX, sizeof(char));
    if(!aux){
        free(response);
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 200 OK\r\n");
    general_headers(&aux);
    strcat(response, aux);
    strcat(response, "Allow: GET,OPTIONS,POST\r\n");
    strcat(response, "Content-Length: 0\r\n\r\n");
    send(clientfd, response, strlen(response), 0);
    return EXIT_SUCCESS;
}

int post_handler(char* path_aux, struct phr_header* headers, size_t num_headers, int clientfd, char* body){
    char* result;
    char abspath[MAXPATH];
    sprintf(abspath, "%s", ABSDIR);
    strcat(abspath, path_aux);//path.ext?dakfjdks
    result = calloc(MAXRESULT, sizeof(char));
    if(!result){
        return EXIT_FAILURE;
    }
    run_script(abspath, body, result);
    send_script_res(result, clientfd);
    free(result);
    return EXIT_SUCCESS;
}

int not_found_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    char sizestr[MAXSIZE];
    int html404, size;
    off_t offset = 0;
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 404 Not Found\r\n");
    general_headers(&response);
    strcat(response, "Content-Length: ");
    html404 = open(DIR404, O_RDONLY);
    if(html404 < 0){
        strcat(response, "0\r\n\r\n");
    }
    else{
        size = get_size(DIR404);
        sprintf(sizestr, "%d", size);
        strcat(response, sizestr);
        strcat(response, "\r\n");
        strcat(response, "Content-Type: text/html\r\n");
        strcat(response, "\r\n\r\n");
    }
    send(clientfd, response, strlen(response), 0);
    printf("\n%s\n", response);
    free(response);
    if(html404 >= 0){
        while(offset < size){
            sendfile(clientfd, html404, &offset, CHUNK);
        }
    }
    if(html404 >= 0)
        close(html404);
    return EXIT_SUCCESS;
}

int method_not_implemented_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 501 Not Implemented\r\n");
    general_headers(&response);
    strcat(response, "\r\n");
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
    strcat(response, "\r\n");
    send(clientfd, response, strlen(response), 0);
    free(response);
    return EXIT_SUCCESS;
}

/*int run_script(char* abspath, char* body, char** result){
    char* ext;
    char* param;
    char command[MAXCOMMAND];
    char script_ext[MAXSCRIPT];
    char file_url[MAXPATH];
    FILE* pipe;
    FILE* fp;
    ext = strrchr(abspath, '.');
    param = strrchr(abspath, '?');
    sprintf(file_url, "%.*s", (int)(param-abspath), abspath);
    if(__file_exists(file_url)){
        return EXIT_FAILURE;
    }
    sprintf(script_ext, "%.*s", (int)(param-ext), ext);
    if(body){
        fp = fopen(SCRTXT, "w");
        fwrite(body, sizeof(char), strlen(body), fp);
        fclose(fp);
    }
    if(!strcmp(script_ext, ".py")){
        sprintf(command, "python3 %s ", file_url);
        strcat(command, param+1);
        strcat(command, " < ");
        if(body){
            strcat(command, SCRTXT);
        }
        else{
            strcat(command, "/dev/null");
        }
        pipe = popen(command, "r");
        fread(*result, sizeof(char), MAXRESULT, pipe);
        pclose(pipe);
    }
    if(!strcmp(script_ext, ".php")){
        sprintf(command, "php %.*s", (int)(param-abspath), abspath);
        strcat(command, " < ");
        if(body){
            strcat(command, SCRTXT);
        }
        else{
            strcat(command, "/dev/null");
        }
        pipe = popen(command, "r");
        fread(*result, sizeof(char), MAXRESULT, pipe);
        pclose(pipe);
    }
    return EXIT_SUCCESS;
}*/

int run_script(char* abspath, char* body, char* result){
    char* ext;
    char* param;
    char *name = NULL;
    char command[MAXCOMMAND];
    FILE* pipe;
    FILE* fp;
    ext = strrchr(abspath, '.');

    if(!__check_ext(ext, ".py"))
        sprintf(command, "python3");
    else if(!__check_ext(ext, ".php"))
        sprintf(command, "php");
    else
        return EXIT_FAILURE;

    if((param = strrchr(abspath, '?')))
        param[0] = ' ';

    strcat(command, " ");
    strcat(command, abspath);

    if(body){
        name = calloc(1, strlen("out38D7EA4C67FFF.txt\0"));
        snprintf(name, strlen("out38D7EA4C67FFF.txt"), "out%lx.txt", pthread_self());
        fp = fopen(name, "w");
        if(!fp){
            free(name);
            return EXIT_FAILURE;
        }
        fwrite(body, sizeof(char), strlen(body), fp);
        fclose(fp);
        strcat(command, " < ");
        strcat(command,  name);
        free(name);
    }else{
        strcat(command, " < /dev/null");
    }
    pipe = popen(command, "r");
    if(!pipe) EXIT_FAILURE;
    fread(result, sizeof(char), MAXRESULT, pipe);
    pclose(pipe);
    return EXIT_SUCCESS;
}

int __check_ext(const char *check, const char *ext){
    while(*check && *ext){
        if(*check != *ext)
            return EXIT_FAILURE;
        check++; ext++;
    }
    return EXIT_SUCCESS;
}

int __file_exists(char *name){
    FILE *fp;
    if(!(fp = fopen(name, "r"))) return EXIT_FAILURE;
    fclose(fp);
    return EXIT_SUCCESS;
}

int check_connection(struct phr_header* headers, int num_headers){
    int i;
    char header[MAXHEADERS], value[MAXVALUE];
    for(i = 0; i < num_headers; i++){
        sprintf(header, "%.*s", (int)headers[i].name_len, headers[i].name);
        if(!strcmp(header, "Connection:")){
            sprintf(value, "%.*s", (int)headers[i].value_len, headers[i].value);
            if(!strcmp(value, "close")){
                return -1;
            }
        }
    }
    return 0;
}

int send_script_res(char* res, int clientfd){
    char response[MAXRESPONSE], http_result[MAXRESULT], len[MAXLEN];
    char* aux;
    aux = calloc(MAXAUX, sizeof(char));
    if(!aux){
        return EXIT_FAILURE;
    }
    sprintf(http_result, "<!DOCTYPE html><html><body>");
    strcat(http_result, res);
    strcat(http_result, "</body></html>");
    sprintf(response, "HTTP/1.1 200 OK\r\n");
    general_headers(&aux);
    strcat(response, aux);
    free(aux);
    sprintf(len, "%ld", strlen(http_result));
    strcat(response, "Content-Length: ");
    strcat(response, len);
    strcat(response, "\r\nContent-Type: text/html");
    strcat(response, "\r\n\r\n");
    strcat(response, http_result);
    if(send(clientfd, response, strlen(response), 0) < 0){
        printf("falló el send\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
