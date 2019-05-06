/*
 * PPROG Game – Morzilla Firefox 2018
 *
 * Authors: Miguel Baquedano, Sergio Cordero, Elias Hernandis
 *          and Rafael Sánchez.
 *
 * Lead author: Elias Hernandis
 */


#include "../includes/error_handling.h"

#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <syslog.h>

void handle_error(const char *error_msg, ...)
{
    if (!error_msg) {
        handle_error("handle_error: called without an error message\n");
        return;
    }

    int num_args = (error_msg[strlen(error_msg) - 1] == '\n') ? 1 : 4;

    va_list args;
    if (num_args > 1) {
        va_start(args, error_msg);
        const char *func_name   = va_arg(args, const char *);
        const char *file_name   = va_arg(args, const char *);
        int line_no             = va_arg(args, int);
        va_end(args);

        // show header of message in yellow
        syslog(LOG_DEBUG, "%s at %s:%d: %s\n", func_name, file_name, line_no, error_msg);
    }
    else
    {
        syslog(LOG_DEBUG, "%s", error_msg);
    }
}

void log_msg(const char *msg, ...)
{

    int num_args = (msg[strlen(msg) - 1] == '\n') ? 1 : 4;

    va_list args;
    if (num_args > 1) {
        va_start(args, msg);
        const char *func_name   = va_arg(args, const char *);
        const char *file_name   = va_arg(args, const char *);
        int line_no             = va_arg(args, int);
        va_end(args);

        handle_error(msg, func_name, file_name, line_no);
    } else
        handle_error(msg);
}

void *oopsalloc(size_t num, size_t size, const char *caller)
{
    void *ptr = calloc(num, size);
    if (!ptr) {
        HE("out of memory! aborting...", caller);
        exit(OOPSALLOC_ERROR);
    }

    return ptr;
}
