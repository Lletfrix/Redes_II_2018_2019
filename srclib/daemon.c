#include <sys/types.h>
#include <unistd.h>
#include <syslog.h>

#include "../includes/daemon.h">

int demonizar(char *service){

    switch (fork()) {
        case -1:
            return(-1);
        case 0:
            break;  //Este es el hijo
        default:
            exit(0);
    }

    if(setsid() == -1){
        //TODO: Handle this
    };
    umask(S_IRWXU | S_IRWXG | S_IRWXO);
    if(!chdir("/")){
        //TODO: Handle this
    };
    int max_fd = getdtablezsize();
    for(int i = 0; i < max_fd; ++i){
        close(i);
    }
    openlog(NULL, LOG_PID, LOG_DAEMON);
    return 0;
}
