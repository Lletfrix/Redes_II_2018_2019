/*
 * PPROG Game – Morzilla Firefox 2018
 *
 * Authors: Miguel Baquedano, Sergio Cordero, Elias Hernandis
 *          and Rafael Sánchez.
 *
 * Lead author: Elias Hernandis
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../includes/config.h"
#include "../includes/error_handling.h"
#include "../includes/lineread.h"

/*
 * Maximum config dictionary size.
 */
#define MAX_DICT_SIZE 250

typedef struct {
    char **keys;
    char **values;
    int size;
} ConfigDict;

/*
 * The global config dictionary (this is the reason you don't need to pass the
 * dictionary around when retrieving configuration options.
 */
ConfigDict *cd;

/*
 * @private
 *
 * Creates a new dictionary. Returns NULL on error.
 */
ConfigDict *_config_dict_new()
{
    ConfigDict *cd = oopsalloc(1, sizeof(ConfigDict), "_config_dict_new");
    cd->keys = oopsalloc(MAX_DICT_SIZE, sizeof(char *), "_config_dict_new");
    cd->values = oopsalloc(MAX_DICT_SIZE, sizeof(char *), "_config_dict_new");

    return cd;
}

/*
 * @private
 *
 * Frees all memory allocated for the given dictionary.
 */
void _config_dict_destroy(ConfigDict *cd)
{
    if (!cd)
        return;

    for (int i = 0; i < cd->size; i++) {
        free(cd->keys[i]);
        free(cd->values[i]);
    }

    free(cd->keys);
    free(cd->values);
    free(cd);
}

/*
 * @private
 *
 * Returns the index of the given key if present on the given dictionary,
 * UINT_ERROR if it isn't found or an error was encountered.
 */
int _config_dict_key_index(ConfigDict *cd, char *key)
{
    if (!cd || !key) {
        HE("invalid parameters", "_config_dict_key_index");
        return UINT_ERROR;
    }

    for (int i = 0; i < cd->size; i++) {
        if (strcmp(cd->keys[i], key) == 0)
            return i;
    }

    return UINT_ERROR;
}

int config_set(char *key, char *value)
{
    if (!key || !value) {
        HE("invalid parameters", "config_set");
        return UINT_ERROR;
    }

    // initialize a dictionary for config if there isn't one already
    if (!cd)
        cd = _config_dict_new();


    int index;
    if ((index = _config_dict_key_index(cd, key)) == UINT_ERROR) {
        if (cd->size >= MAX_DICT_SIZE) {
            HE("no more config items fit into the config dictionary, increase MAX_DICT_SIZE", "config_set");
            return UINT_ERROR;
        }

        index = cd->size;

        cd->keys[index] = oopsalloc(strlen(key) + 1, sizeof(char), "config_set");
        cd->values[index] = oopsalloc(strlen(value) + 1, sizeof(char), "config_set");

        cd->size++;
    }



    // copy k&v and increase dict size
    strcpy(cd->keys[index], key);
    strcpy(cd->values[index], value);

    return cd->size;
}


char *config_get(char *key)
{
    if (!key) {
        HE("invalid parameters – key must not be NULL", "config_get");
        return NULL;
    }

    if (!cd)
        return NULL;

    int index = _config_dict_key_index(cd, key);
    if (index != UINT_ERROR) {
        return cd->values[index];
    }

    return NULL;
}

int config_get_int(char *key)
{
    char *val = config_get(key);
    if (!val) {
        HE("key not found", "config_get_int");
        return 0;
    }

    return atoi(val);
}

int load_config_from_file(const char *config_file)
{
    if (!config_file) {
        HE("invalid parameters", "load_config_from_file");
        return UINT_ERROR;
    }

    FILE *f = fopen(config_file, "r");
    if (!f) {
        HE("could not open config file", "load_config_from_file");
        return UINT_ERROR;
    }
    char *key;
    char *value;
    while ((key = fgetll(f)))
    {
        if (!(value = fgetll(f))) {
            HE("invalid config file. found a key without an associated value", "load_config_from_file");
            free(key);
            return UINT_ERROR;
        }

        if (!config_set(key, value)) {
            HE("could not store given key in dictionary", "load_config_from_file");
            free(key); free(value);
            return UINT_ERROR;
        }
        free(key);
        free(value);
    }

    fclose(f);

    return cd->size;
}

void config_destroy()
{
    if (cd)
        _config_dict_destroy(cd);
}
