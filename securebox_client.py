import argparse as arg

parser = arg.ArgumentParser(description = 'Cliente para realizar diversas acciones en el servidor SecureBox')
group = parser.add_mutually_exclusive_group()
group.add_argument('--create_id', nargs='*')
group.add_argument('--search_id', nargs=1)
group.add_argument('--delete_id', nargs=1)
group.add_argument('--upload', nargs=1)
parser.add_argument('--source_id', nargs=1)
parser.add_argument('--dest_id', nargs=1)
group.add_argument('--list_files', action='store_true', nargs=0)
group.add_argument('--download', nargs=1)
group.add_argument('--delete_file', nargs=1)
group.add_argument('--encrypt', nargs=1)
group.add_argument('--sign', nargs=1)
group.add_argument('--enc_sign', nargs=1)

args = parser.parse_args()
