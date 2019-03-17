import argparse as arg
import json as js
import requests as req
from functionalities import * 

parser = arg.ArgumentParser(description = 'Cliente para realizar diversas acciones en el servidor SecureBox')
parser.add_argument('--source_id', nargs=1)
parser.add_argument('--dest_id', nargs=1)
group = parser.add_mutually_exclusive_group()
group.add_argument('--create_id', nargs='*')
group.add_argument('--search_id', nargs=1)
group.add_argument('--delete_id', nargs=1)
group.add_argument('--upload', nargs=1)
group.add_argument('--list_files', action='store_true')
group.add_argument('--download', nargs=1)
group.add_argument('--delete_file', nargs=1)
group.add_argument('--encrypt', nargs=1)
group.add_argument('--sign', nargs=1)
group.add_argument('--enc_sign', nargs=1)

args = parser.parse_args()
if args.create_id:
    if len(args.create_id) == 2:
        create_id_routine(args.create_id[0], args.create_id[1])
    elif len(args.create_id) == 3:
        create_id_routine(args.create_id[0], args.create_id[1], args.create_id[2])
    else:
        print('create_id requires 2 or 3 arguments\n')
        parser.print_help()
elif args.search_id:
    print('shit\n')
    #search_id routine
elif args.delete_id:
    delete_id_routine(args.delete_id[0])
elif args.upload:
    print('shit\n')
    #upload routine
elif args.list_files:
    print('shit\n')
    #list_files routine
elif args.download:
    print('shit\n')
    #download routine
elif args.delete_file:
    print('shit\n')
    #delete_file routine
elif args.encrypt:
    print('shit\n')
    #encrypt routine
elif args.sign:
    print('shit\n')
    #sign routine
elif args.enc_sign:
    print('shit\n')
    #enc_sign routine
else:
    parser.print_help()
