#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <syslog.h>
#include <signal.h>
#include <stdlib.h>
#include "../includes/daemon.h"

int demonizar(const char *service, char* cwd){
    signal(SIGPIPE, SIG_IGN);
    switch (fork()) {
        case -1:
            return -1;
        case 0:
            break;  //Este es el hijo
        default:
            exit(0);
    }

    if(setsid() == -1){
        return -1;
    };
    umask(S_IRWXU | S_IRWXG | S_IRWXO);
    getcwd(cwd, PATHMAX);
    if(!chdir("/")){
        return -1;
    };
    int n_fd = getdtablesize();
    for(int i = 0; i < n_fd; ++i){
        close(i);
    }
    openlog(service, LOG_PID, LOG_DAEMON);
    return 0;
}
