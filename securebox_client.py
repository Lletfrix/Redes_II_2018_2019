import argparse as arg
from functionalities import *
import sys

tok = open('token.txt', 'r')
tokenstr = tok.read()
if tokenstr[-1] is '\n':
    tokenstr = tokenstr[:-1]
headers['authorization'] = 'Bearer ' + tokenstr
keypath = 'private_key.pem'



def load_private_key():
    f = open(keypath, 'rb')
    print('Leyendo su clave privada...', end='')
    private_key = RSA.import_key(f.read())
    print('OK')
    return private_key

def load_public_key(user_id):
    print('Obteniendo clave pública del destinatario...', end='')
    pkPEM = get_publicKey(user_id)
    print('OK')
    public_key = RSA.import_key(pkPEM)
    return public_key


parser = arg.ArgumentParser(description = 'Cliente para realizar diversas acciones en el servidor SecureBox')
parser.add_argument('--source_id', nargs=1)
parser.add_argument('--dest_id', nargs=1)
actions = parser.add_mutually_exclusive_group(required=True)
actions.add_argument('--create_id', nargs='*')
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
if args.create_id:
    if len(args.create_id) == 2:
        key = create_id_routine(args.create_id[0], args.create_id[1])
    elif len(args.create_id) == 3:
        key = create_id_routine(args.create_id[0], args.create_id[1], args.create_id[2])
    else:
        print('create_id requires 2 or 3 arguments\n')
        parser.print_help()
        exit()
    if key is not None:
        f = open(keypath, 'wb')
        f.write(key.exportKey())
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
