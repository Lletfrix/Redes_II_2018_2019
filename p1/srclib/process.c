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
#include <syslog.h>
#include <pthread.h>
#include "../includes/picohttpparser.h"
#include "../includes/process.h"
#include "../includes/config.h"

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

int get_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int post_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd, char* body);
int options_handler(char* path, struct phr_header* headers, size_t num_headers, int clientfd);
int bad_request_response(int clientfd);
int method_not_implemented_response(int clientfd);
int not_found_response(int clientfd);
int internal_error_response(int clientfd);
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
        //If we receive an empty package or recv fails
        if(len <= 0){
            return EXIT_SUCCESS;
        }
        num_headers = sizeof(headers) / sizeof(headers[0]);
        //Parsing of the request with picoparser
        pret = phr_parse_request(buf, len, &method, &method_len, &path, &path_len,
                                &minor_version, headers, &num_headers, prevbuflen);
        //If the request is malformed, 400 Bad Request
        if(pret < 0){
            return bad_request_response(clientfd);
        }
        //We close connection if we receive close header or if the version is 1.0
        if(check_connection(headers, num_headers) || minor_version == 0){
            keep_alive=0;
        }
        sprintf(method_aux, "%.*s", (int)method_len, method);
        sprintf(path_aux, "%.*s", (int)path_len, path);
        //Execute the routine of the proper verb
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
        //If there was a mistake executing the routine, 500 Internal Server Error
        if(errcode){
            keep_alive = 0;
            internal_error_response(clientfd);
        }
    }
    return method_not_implemented_response(clientfd);
}
//Function that obtains the size of a file indicated by path
int get_size(char* path){
    struct stat atrib;
    stat(path, &atrib);
    return atrib.st_size;
}
//Function that returns the current UTC time in res
int gmt_time_http(char** res, int tam){
    char timeaux[MAXTIME];
    time_t act = time(0);
    struct tm tm = *gmtime(&act);
    strftime(timeaux, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    strcat(*res, timeaux);
    return 1;
}
//Function that returns the basic headers of a HTTP request in res(Date and Server)
int general_headers(char** res){
    strcat(*res, "Date: ");
    gmt_time_http(res, MAXAUX);
    strcat(*res, "\r\n");
    strcat(*res, "Server: ");
    strcat(*res, config_get("server_signature"));
    strcat(*res, "\r\n");
    return 1;
}
//Function that returns the last time 'path' file was modified, and returns it into res
int last_modified_http(char* path, char** res, int tam){
    struct tm tm;
    struct stat atrib;
    stat(path, &atrib);
    tm = *gmtime(&(atrib.st_mtime));
    strftime(*res, tam, "%a, %d %b %Y %H:%M:%S %Z", &tm);
    return 1;
}
//Function that returns the mime type of a given extension(ext) in res
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
//Function that processes a HTTP GET request
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
    strcat(abspath, config_get("cwd"));
    strcat(abspath, config_get("server_root"));
    if(!strcmp(path, "/")){
        strcat(path, "index.html");
    }
    strcat(abspath, path);
    ext = strrchr(path, '.');
    //Gets type of request
    if(!get_type(ext, type) && !strrchr(ext,'?')){
        //404 not found if we dont support the extension and it is not a script
        not_found_response(clientfd);
        free(aux);
        free(response);
        free(type);
        return EXIT_SUCCESS;
    }
    //Launch if script
    if(strrchr(ext, '?')){
        //Check if it is Python or PHP, otherwise 404
        sprintf(script_ext, "%.*s", (int)(strrchr(ext, '?') - ext), ext);
        if(!strcmp(script_ext, ".py") || !strcmp(script_ext, ".php")){
            result = calloc(MAXRESULT, sizeof(char));
            if(!result){
                free(aux);
                free(response);
                free(type);
                return EXIT_FAILURE;
            }
            //Execute the script and send the results via HTTP
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
    //Build response
    size = get_size(abspath);
    strcat(response, "HTTP/1.1 200 OK\r\n");
    //Headers
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
    //Body
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
//Function that processes an OPTION HTTP Request
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
    //Build and send HTTP Response
    strcat(response, "HTTP/1.1 200 OK\r\n");
    general_headers(&aux);
    strcat(response, aux);
    strcat(response, "Allow: GET,OPTIONS,POST\r\n");
    strcat(response, "Content-Length: 0\r\n\r\n");
    send(clientfd, response, strlen(response), 0);
    return EXIT_SUCCESS;
}
//Function that processes a POST HTTP Request
int post_handler(char* path_aux, struct phr_header* headers, size_t num_headers, int clientfd, char* body){
    char* result;
    char abspath[MAXPATH];
    //Go to the original directory
    sprintf(abspath, "%s", config_get("cwd"));
    strcat(abspath, config_get("server_root"));
    //sprintf(abspath, "%s", config_get("server_root"));
    strcat(abspath, path_aux); //Add the path of the requested script
    result = calloc(MAXRESULT, sizeof(char));
    if(!result){
        return EXIT_FAILURE;
    }
    //Run script and send results via HTTP
    run_script(abspath, body, result);
    send_script_res(result, clientfd);
    free(result);
    return EXIT_SUCCESS;
}
//Function that builds and sends a 404 customizable response
int not_found_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    char sizestr[MAXSIZE];
    char abspath[MAXPATH]={0};
    int html404, size;
    off_t offset = 0;
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 404 Not Found\r\n");
    //Add the common headers
    general_headers(&response);
    strcat(response, "Content-Length: ");

    strcat(abspath, config_get("cwd"));
    strcat(abspath, config_get("server_root"));
    strcat(abspath, config_get("404file"));

    html404 = open(abspath, O_RDONLY);
    //If there is no 404 file, we send just the headers
    if(html404 < 0){
        strcat(response, "0\r\n\r\n");
        syslog(LOG_INFO, "No 404 file found on path: %s", abspath);
    }
    else{
        size = get_size(abspath);
        sprintf(sizestr, "%d", size);
        strcat(response, sizestr);
        strcat(response, "\r\n");
        strcat(response, "Content-Type: text/html\r\n\r\n");
    }
    //Send response
    send(clientfd, response, strlen(response), 0);
    free(response);
    //Send custom 404 page
    if(html404 >= 0){
        while(offset < size){
            sendfile(clientfd, html404, &offset, CHUNK);
        }
    }
    //Close the descriptor
    if(html404 >= 0)
        close(html404);
    return EXIT_SUCCESS;
}
//Function that builds and sends a 501 Method Not Implemented response
int method_not_implemented_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 501 Not Implemented\r\n");
    //Common headers
    general_headers(&response);
    strcat(response, "\r\n");
    //Send response
    send(clientfd, response, strlen(response), 0);
    free(response);
    return EXIT_SUCCESS;
}
//Function that builds and sends a 400 Bad Request response
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
//Function that builds and sends a customizable 500 Internal Server Error response
int internal_error_response(int clientfd){
    char* response = calloc(MAXRESPONSE, sizeof(char));
    char sizestr[MAXSIZE];
    int html500, size;
    char abspath[MAXPATH];
    off_t offset = 0;
    if(!response){
        return EXIT_FAILURE;
    }
    strcat(response, "HTTP/1.1 500 Internal Server Error\r\n");
    //Common headers
    general_headers(&response);
    strcat(response, "Content-Length: ");
    //Try to open 500 custom page
    strcat(abspath, config_get("cwd"));
    strcat(abspath, config_get("server_root"));
    strcat(abspath, config_get("500file"));


    html500 = open(abspath, O_RDONLY);
    if(html500 < 0){
        //If the file doesn't exist, we send just the headers
        strcat(response, "0\r\n\r\n");
    }
    else{
        size = get_size(abspath);
        sprintf(sizestr, "%d", size);
        strcat(response, sizestr);
        strcat(response, "\r\n");
        strcat(response, "Content-Type: text/html\r\n\r\n");
    }
    //Send the response
    send(clientfd, response, strlen(response), 0);
    free(response);
    //Send the custom page
    if(html500 >= 0){
        while(offset < size){
            sendfile(clientfd, html500, &offset, CHUNK);
        }
    }
    if(html500 >= 0)
        close(html500);
    free(response);
    return EXIT_SUCCESS;
}
//Function that executes the requested script and writes its output in an aux file
int run_script(char* abspath, char* body, char* result){
    char* ext;
    char* param;
    char *name = NULL;
    char command[MAXCOMMAND];
    FILE* pipe;
    FILE* fp;
    ext = strrchr(abspath, '.');
    //Check if we support the language
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
    //See if it has any argument
    if(body){
        //38D7EA4C67FFF is the biggest thread identifier, we take it as a reference
        //File in which the system will write the output
        name = calloc(1, MAXPATH/4 + strlen("out38D7EA4C67FFF.txt\0"));
        snprintf(name, MAXPATH/4 + strlen("out38D7EA4C67FFF.txt"), "%s%sout%lx.txt", config_get("cwd"), config_get("temp_dir"),pthread_self());
        fp = fopen(name, "w");
        //fopen debugging by syslog
        if(!fp){
            syslog(LOG_DEBUG, "Couldn't open file: %s. Are you sure you are running this with super user rights??", name);
            free(name);
            return EXIT_FAILURE;
        }
        //Finish the build of the command
        fwrite(body, sizeof(char), strlen(body), fp);
        fclose(fp);
        strcat(command, " < ");
        strcat(command,  name);
        free(name);
    }else{
        //No arguments
        strcat(command, " < /dev/null");
    }
    //Execute the script
    syslog(LOG_DEBUG, "%lu: Going to run command: %s", pthread_self(), command);
    pipe = popen(command, "r");
    if(!pipe) EXIT_FAILURE;
    fread(result, sizeof(char), MAXRESULT, pipe);
    pclose(pipe);
    return EXIT_SUCCESS;
}
//Function that compares two strings(In particular, two extensions)
int __check_ext(const char *check, const char *ext){
    while(*check && *ext){
        if(*check != *ext)
            return EXIT_FAILURE;
        check++; ext++;
    }
    return EXIT_SUCCESS;
}
//Function that checks whether a file exists or not
int __file_exists(char *name){
    FILE *fp;
    if(!(fp = fopen(name, "r"))) return EXIT_FAILURE;
    fclose(fp);
    return EXIT_SUCCESS;
}
//Function that checks if there is a header telling us to close the connection
//after processing the request
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
//Function that sends the result of the script executed before we call this to the client
int send_script_res(char* res, int clientfd){
    char response[MAXRESPONSE], http_result[MAXRESULT], len[MAXLEN];
    char* aux;
    aux = calloc(MAXAUX, sizeof(char));
    if(!aux){
        return EXIT_FAILURE;
    }
    //HTTP formatted result, not just plain
    sprintf(http_result, "<!DOCTYPE html><html><body>");
    strcat(http_result, res);
    strcat(http_result, "</body></html>");
    //HTTP response
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
    //Send full response
    if(send(clientfd, response, strlen(response), 0) < 0){
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
