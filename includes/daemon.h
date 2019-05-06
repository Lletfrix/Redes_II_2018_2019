#ifndef DAEMON_H
#define DAEMON_H



#define PATHMAX 1024
/**
* FUNCIÓN:     int demonizar(char *service)
* ARGS_IN:     char *service - identificador del servicio.
*              char *cwd     - direccion de memoria donde se almacena el cwd
* DESCRIPCIÓN: pasa el proceso a modo demonio. Lo ejecuta en segundo plano.
* ARGS_OUT:    int - devuelve 0 en ejecución correcta. Devuelve un entero
*              negativo en caso de error.
*/
int demonizar(const char *service, char *cwd);

#endif
