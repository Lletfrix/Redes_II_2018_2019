import argparse as arg
from functionalities import *
from pathlib import Path
from shutil import copy
from os import mkdir, path
import sys

#Variables auxiliares para soportar los diferentes alias
defpath = 'Alias/default/'
keyfile = 'private_key.pem'
tokfile = 'token.txt'
tokpath = defpath + tokfile
keypath = defpath + keyfile


# Función que carga la clave privada del usuario por defecto, que es donde estará
# la identidad cargada previamente con la función load_alias(alias)
# output Clave privada del usuario por defecto
def load_private_key():
    f = open(keypath, 'rb')
    print('Leyendo su clave privada...', end='')
    private_key = RSA.import_key(f.read()) #Cargamos la clave privada del directorio por defecto
    print('OK')
    return private_key

# Función que obtiene la clave pública de un usuario especificado
# input user_id ID del user a obtener su clave pública
# output Clave pública obtenida, nada en caso de que haya error
def load_public_key(user_id):
    print('Obteniendo clave pública del destinatario...', end='')
    pkPEM = get_publicKey(user_id)  #Se obtiene la clave pública del servidor
    if pkPEM is None:
        return
    print('OK')
    public_key = RSA.import_key(pkPEM)  #Importamos como clave pública con Crypto
    return public_key

# Función que carga un alias, es decir, establece cual de las identidades locales se usará
# input alias Alias a cargar en la carpeta default
def load_alias(alias):
    print('Cargando token y clave privada del usuario',alias,'en el usuario por defecto...', end='')
    copy('Alias/'+alias+'/'+keyfile, keypath)
    copy('Alias/'+alias+'/'+tokfile, tokpath)
    print('OK')

# Función que carga el token para poder realizar cualquier petición al servidor
# input token Ruta del token a cargar
def load_auth(token):
    tok = open(token, 'r')
    tokenstr = tok.read()
    if tokenstr[-1] is '\n':
        tokenstr = tokenstr[:-1]
    headers['authorization'] = 'Bearer ' + tokenstr

if __name__ == '__main__':

    #Estructura de parseo de argumentos
    parser = arg.ArgumentParser(description = 'Cliente para realizar diversas acciones en el servidor SecureBox.\
                                            Si tiene dudas sobre el funcionamiento del programa o sobre los argumentos \
                                            por favor visite https://vega.ii.uam.es/2302-02-19/practica2/wikis/tutorial.')
    parser.add_argument('--source_id', nargs=1) #Indica el remitente del fichero a descargar
    parser.add_argument('--dest_id', nargs=1)   #Indica el destinatario del fichero a subir
    # Ejecutamos uno, y solo un, comando por ejecución del programa
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--create_id', nargs='*')  #Puede tener 2 ó 3 argumentos, lo comprobamos más adelante
    actions.add_argument('--load_id', nargs=1)
    actions.add_argument('--search_id', nargs=1)
    actions.add_argument('--delete_id', nargs=1)
    actions.add_argument('--upload', nargs=1)
    actions.add_argument('--list_files', action='store_true')   #List files no necesita argumentos
    actions.add_argument('--download', nargs=1)
    actions.add_argument('--delete_file', nargs=1)
    actions.add_argument('--encrypt', nargs=1)
    actions.add_argument('--sign', nargs=1)
    actions.add_argument('--enc_sign', nargs=1)


    args = parser.parse_args(sys.argv[1:])  #El primer argumento es el nombre del programa

    # Comprobamos si hay una identidad válida en el directorio por defecto
    try:
        load_auth(tokpath)
    except FileNotFoundError:
        if args.create_id or args.load_id:  #Salvo que esté intentado crearla o cargarla para usarla luego
            pass
        else:
            print('No hay una identidad por defecto, por favor, carga o crea una con --load_id o --create_id')
            exit()

    #Creación de identidad
    if args.create_id:
        #Si son dos parámetros, el usuario quiere registar en el servidor una identidad con el token que hay en el directorio por defecto
        if len(args.create_id) == 2:
            if not Path(tokpath).is_file():
                print('No existe un token por defecto, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- default\n        |-- token.txt')
                exit()
            key = create_id_routine(args.create_id[0], args.create_id[1])
            #Si no ha habido error, guardamos la clave
            if key is not None:
                f = open(keypath, 'wb')
                f.write(key.exportKey())
                f.flush()
        #Si son tres parámetros, el usuario quiere registrar en el servidor una identidad con el token de un alias local
        elif len(args.create_id) == 3:
            dstKey = 'Alias/'+args.create_id[2]+'/'+keyfile
            dstTok = 'Alias/'+args.create_id[2]+'/'+tokfile
            if not Path(dstKey).is_file():
                if not Path(dstTok).is_file():  #Si no hay token, informamos al usuario
                    print('No existe token para el alias introducido, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- '+args.create_id[2]+'\n        |-- token.txt')
                    try:
                        mkdir('Alias'+'/'+args.create_id[2])    #Intentamos crear la carpeta para ese alias
                    except FileExistsError:
                        pass
                    exit()
                #Si hay token pero no tiene clave pública, registramos la identidad
                load_auth(dstTok)
                key = create_id_routine(args.create_id[0], args.create_id[1])
                f = open(dstKey, 'wb')
                f.write(key.exportKey())
                f.flush()
            #Cargamos dicha identidad en el directorio por defecto
            load_alias(args.create_id[2])
        else:   #Error si hay un número de argumentos distinto de 2 ó 3
            print('create_id requiere 2 o 3 argumentos\n')
            parser.print_help()
            exit()

    #Carga de identidad
    elif args.load_id:
        alias = args.load_id[0]
        dstKey = 'Alias/'+alias+'/'+keyfile
        dstTok = 'Alias/'+alias+'/'+tokfile
        if not Path(dstKey).is_file():
            if not Path(dstTok).is_file():  #Si no hay token no es una identidad válida
                print('No existe token para el alias introducido, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- '+alias+'\n        |-- token.txt')
                try:
                    mkdir('Alias'+'/'+alias)    #Intentamos crear la carpeta para ese alias
                except FileExistsError:
                    pass
                exit()
            #Si no tiene clave privada, le informamos de que primero registre la identidad en el servidor
            print('El alias introducido no dispone de una clave privada, por favor, cree la suya ejecutando el programa con el parámetro --create_id')
            exit()
        load_alias(alias)   #Cargamos la identidad en la carpeta por defecto

    #Búsqueda de usuarios
    elif args.search_id:
        #Realizamos la petición al servidor
        found = search_id_routine(args.search_id[0])
        if found:
            print(len(found), ' usuarios encontrados')
            print_found_users(found)

    #Borrado de la identidad contenida en la carpeta por defecto
    elif args.delete_id:
        delete_id_routine(args.delete_id[0])

    #Subida de ficheros
    elif args.upload:
        if(args.dest_id):
            private_key = load_private_key()
            public_key = load_public_key(args.dest_id[0])  #Obtenemos claves
            upload_routine(args.upload[0], private_key, public_key)
        else:   #Error si no se especifica destinatario
            print('El parámetro --dest_id es necesario para poder subir el fichero')
            parser.print_help()

    #Listado de ficheros
    elif args.list_files:
        found = list_files_routine()    #Obtenemos el listado
        if found:
            print(len(found['files_list']), 'ficheros encontrados')
            print_found_files(found['files_list'])  #Imprimimos todos los ficheros

    #Descarga
    elif args.download:
        if(args.source_id):
            private_key = load_private_key()
            public_key = load_public_key(args.source_id[0]) #Obtenemos las claves necesarias
            download_routine(args.download[0], private_key, public_key)
        else:   #Error si no se especifica el destinatario
            print('El parámetro --source_id es necesario para poder descargar el fichero')
            parser.print_help()

    #Borrado de fichero
    elif args.delete_file:
        delete_file_routine(args.delete_file[0])

    #Cifrado en local
    elif args.encrypt:
        private_key = load_private_key()
        public_key = load_public_key(args.dest_id[0])   #Obtenemos las claves
        encrypt_routine(args.encrypt[0], private_key, public_key)

    #Firma en local
    elif args.sign:
        private_key = load_private_key()    #Obtenemos la clave
        sign_routine(args.sign[0], private_key)

    #Firma y cifrado en local
    elif args.enc_sign:
        private_key = load_private_key()
        public_key = load_public_key(args.dest_id[0])   #Obtenemos las claves
        enc_sign_routine(args.enc_sign[0], private_key, public_key)

    #En cualquier otro caso, imprimimos las instrucciones del parser
    else:
        parser.print_help()
