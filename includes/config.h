/**
 * @brief Configuration storage module.
 *
 * This module provides a common interface to store general settings. 
 * Configuration items can be stored dynamically or be loaded from a file.
 * All configuration options are available throughout every lib file, so take 
 * care of avoiding key collisions, for example by prefixing your keys.
 *
 * @file config.h
 * @author Elías Hernandis, Rafael Sánchez, Sergio Cordero, Miguel Baquedano
 * @version 1.0
 * @date 17-01-2018
 */

#ifndef __CONFIG_H__
#define __CONFIG_H__
/** @defgroup config Config module
*
 * This module provides a common interface to store general settings. 
 * Configuration items can be stored dynamically or be loaded from a file.
 * All configuration options are available throughout every lib file, so take 
 * care of avoiding key collisions, for example by prefixing your keys.
*/

/**
 * Stores a key-value pair in the config dictionary. Returns UINT_ERROR on
 * error. If the given key was already stored, it's value is overriden by the
 * new one.
 *
 * @ingroup config
 * @param key key to be stored
 * @param value value associated with key to be stored
 * @return error code
 */
int config_set(char *key, char *value);


/**
 * Returns the value associated with the given key, NULL on error.
 *
 * @ingroup config
 * @param key key from which to get the value from
 * @return value
 */
char *config_get(char *key);

/**
 * Returns the value associated with the given key, but casted to an int.
 * Casting is done by calling atoi(). On error, 0 will be returned.
 *
 * @ingroup config
 * @param key key from which to get the value from
 * @return error code
 */
int config_get_int(char *key);

/**
 * Loads configuration from the given filename. Returns UINT_ERROR on error.
 *
 * @ingroup config
 * @param config_file configuration file's path
 */
int load_config_from_file(const char *config_file);


/**
 * Frees all resources allocated by the config module.
 * @ingroup config
 */
void config_destroy();
#endif
