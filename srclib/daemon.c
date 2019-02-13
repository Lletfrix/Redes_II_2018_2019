#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <syslog.h>
#include <stdlib.h>
#include "../includes/daemon.h"

int demonizar(const char *service){

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
    int n_fd = getdtablesize();
    for(int i = 0; i < n_fd; ++i){
        close(i);
    }
    openlog(service, LOG_PID, LOG_DAEMON);
    return 0;
}
