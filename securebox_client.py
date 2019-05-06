import argparse as arg
from functionalities import *
from pathlib import Path
from shutil import copy
from os import mkdir, path
import sys

defpath = 'Alias/default/'
keyfile = 'private_key.pem'
tokfile = 'token.txt'
tokpath = defpath + tokfile
keypath = defpath + keyfile



def load_private_key():
    f = open(keypath, 'rb')
    print('Leyendo su clave privada...', end='')
    private_key = RSA.import_key(f.read())
    print('OK')
    return private_key

def load_public_key(user_id):
    print('Obteniendo clave pública del destinatario...', end='')
    pkPEM = get_publicKey(user_id)
    if pkPEM is None:
        return
    print('OK')
    public_key = RSA.import_key(pkPEM)
    return public_key

def load_alias(alias):
    print('Cargando token y clave privada del usuario',alias,'en el usuario por defecto...', end='')
    copy('Alias/'+alias+'/'+keyfile, keypath)
    copy('Alias/'+alias+'/'+tokfile, tokpath)
    print('OK')

def load_auth(token):
    tok = open(token, 'r')
    tokenstr = tok.read()
    if tokenstr[-1] is '\n':
        tokenstr = tokenstr[:-1]
    headers['authorization'] = 'Bearer ' + tokenstr

if __name__ == '__main__':

    parser = arg.ArgumentParser(description = 'Cliente para realizar diversas acciones en el servidor SecureBox')
    parser.add_argument('--source_id', nargs=1)
    parser.add_argument('--dest_id', nargs=1)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--create_id', nargs='*')
    actions.add_argument('--load_id', nargs=1)
    actions.add_argument('--search_id', nargs=1)
    actions.add_argument('--delete_id', nargs=1)
    actions.add_argument('--upload', nargs=1)
    actions.add_argument('--list_files', action='store_true')
    actions.add_argument('--download', nargs=1)
    actions.add_argument('--delete_file', nargs=1)
    actions.add_argument('--encrypt', nargs=1)
    actions.add_argument('--sign', nargs=1)
    actions.add_argument('--enc_sign', nargs=1)


    args = parser.parse_args(sys.argv[1:])

    try:
        load_auth(tokpath)
    except FileNotFoundError:
        if args.create_id or args.load_id:
            pass
        else:
            print('No hay una identidad por defecto, por favor, carga o crea una con --load_id o --create_id')
            exit()

    if args.create_id:
        if len(args.create_id) == 2:
            if not Path(tokpath).is_file():
                print('No existe un token por defecto, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- default\n        |-- token.txt')
                exit()
            key = create_id_routine(args.create_id[0], args.create_id[1])
            if key is not None:
                f = open(keypath, 'wb')
                f.write(key.exportKey())
                f.flush()

        elif len(args.create_id) == 3:
            dstKey = 'Alias/'+args.create_id[2]+'/'+keyfile
            dstTok = 'Alias/'+args.create_id[2]+'/'+tokfile
            if not Path(dstKey).is_file():
                if not Path(dstTok).is_file():
                    print('No existe token para el alias introducido, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- '+args.create_id[2]+'\n        |-- token.txt')
                    try:
                        mkdir('Alias'+'/'+args.create_id[2])
                    except FileExistsError:
                        pass
                    exit()
                load_auth(dstTok)
                key = create_id_routine(args.create_id[0], args.create_id[1])
                f = open(dstKey, 'wb')
                f.write(key.exportKey())
                f.flush()

            load_alias(args.create_id[2])
        else:
            print('create_id requiere 2 o 3 argumentos\n')
            parser.print_help()
            exit()

    elif args.load_id:
        alias = args.load_id[0]
        dstKey = 'Alias/'+alias+'/'+keyfile
        dstTok = 'Alias/'+alias+'/'+tokfile
        if not Path(dstKey).is_file():
            if not Path(dstTok).is_file():
                print('No existe token para el alias introducido, por favor, añada el archivo token.txt en la siguiente ruta:\n'+'.\n|-- Alias\n    |-- '+alias+'\n        |-- token.txt')
                try:
                    mkdir('Alias'+'/'+alias)
                except FileExistsError:
                    pass
                exit()
            print('El alias introducido no dispone de una clave privada, por favor, cree la suya ejecutando el programa con el parámetro --create_id')
            exit()
        load_alias(alias)


    elif args.search_id:
        found = search_id_routine(args.search_id[0])
        if found:
            print(len(found), ' usuarios encontrados')
            print_found_users(found)


    elif args.delete_id:
        delete_id_routine(args.delete_id[0])


    elif args.upload:
        if(args.dest_id):
            private_key = load_private_key()
            public_key = load_public_key(args.dest_id[0])
            upload_routine(args.upload[0], private_key, public_key)
        else:
            print('El parámetro --dest_id es necesario para poder subir el fichero')
            parser.print_help()


    elif args.list_files:
        found = list_files_routine()
        if found:
            print(len(found['files_list']), 'ficheros encontrados')
            print_found_files(found['files_list'])


    elif args.download:
        if(args.source_id):
            private_key = load_private_key()
            public_key = load_public_key(args.source_id[0])
            download_routine(args.download[0], private_key, public_key)
        else:
            print('El parámetro --source_id es necesario para poder descargar el fichero')
            parser.print_help()


    elif args.delete_file:
        delete_file_routine(args.delete_file[0])


    elif args.encrypt:
        private_key = load_private_key()
        public_key = load_public_key(args.dest_id[0])
        encrypt_routine(args.encrypt[0], private_key, public_key)


    elif args.sign:
        private_key = load_private_key()
        sign_routine(args.sign[0], private_key)


    elif args.enc_sign:
        private_key = load_private_key()
        public_key = load_public_key(args.dest_id[0])
        enc_sign_routine(args.enc_sign[0], private_key, public_key)


    else:
        parser.print_help()
