import requests as req
from Crypto.PublicKey import RSA
import json
import os
from document_sign import *

api_url = 'http://vega.ii.uam.es:8080/api/'
headers = {'content-type': 'application/json', 'authorization': None}
endpoints = {'create':'users/register', 'userdelete':'users/delete', 'search':'users/search',
              'getpk':'users/getPublicKey', 'up':'files/upload', 'dwn':'files/download',
               'list':'files/list', 'filedelete':'files/delete'}

def build_url(key):
    return api_url+endpoints[key]

def create_id_routine(name, email, alias=None): #alias sirve para algo?
    print('Generando par de claves RSA de 2048 bits...', end='')
    rsaKey = RSA.generate(2048)
    pkPEM = rsaKey.publickey().exportKey().decode('ascii') #Get pem format

    totalName = name+'#'+alias if alias else name #Concatenate alias if available
    print('OK')

    params = {'nombre': totalName, 'email': email, 'publicKey': pkPEM}
    url = build_url('create')
    resp = req.post(url, json=params, headers=headers)

    code = code_checker(resp)
    if code is 200:
        jresp = resp.json()
        found = search_users_on_sv(jresp['nombre'])
        if code_checker(found) is 200:
            jfound = found.json()
            for rec in jfound:
                if rec['nombre'] == jresp['nombre'] and rec['email'] == email and\
                   rec['publicKey'] == pkPEM:
                   print('Identidad con ID#' +  rec['userID'] + ' creada correctamente')
                   break
        return rsaKey
    return None

def delete_id_routine(userID):
    print('Borrando usuario con ID#', userID, '...', end='')
    params = {'userID':userID}
    url = build_url('userdelete')
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        print('OK')

def upload_routine(path, private_key, public_key):
    if os.path.isfile(path):
        url = build_url('up')
        up_headers = dict(headers)
        up_headers.pop('content-type') #Quitamos el content-type json
        #Encrypt
        print('Obteniendo fichero...', end='')
        doc = docusign(path)
        print('OK')
        print('Generando firma digital...', end='')
        doc.get_digital_sign(private_key)
        print('OK')
        print('Cifrando fichero...', end='')
        doc.cipher(private_key)
        print('OK')
        print('Generando sobre digital...', end='')
        doc.get_digital_envelope(public_key)
        print('OK')
        print('Subiendo fichero...', end='')
        doc.prepare_upload()
        #Send file
        files = {'ufile': (path, doc.ciphered)}
        resp = req.post(url, headers=up_headers, files=files)
        code = code_checker(resp)
        if code is 200:
            print('OK')
        #TODO: Checkings and print file_id
    else:
        print('La ruta proporcionada es incorrecta')


def search_id_routine(string):
    print('Buscando coincidencias con: <<', string,'>> en el servidor')
    params={'data_search':string}
    url = build_url('search')
    resp = search_users_on_sv(string)
    code = code_checker(resp)
    if code is 200:
        print('OK')
        return resp.json()
    return None

def list_files_routine():
    print('Obteniendo la lista de ficheros subidos...', end='')
    url = build_url('list')
    resp = req.post(url, headers=headers)
    code = code_checker(resp)
    if code is 200:
        print('OK')
        return resp.json()
    return None

def download_routine(fileid, private_key, public_key):
    print('Obteniendo el fichero del servidor...', end='')
    url = build_url('dwn')
    params = {'file_id':fileid}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        #Decrypt
        doc = docusign(None, resp.content)
        doc.get_session_key(private_key)
        doc.decipher()
        if not doc.verify_signature(public_key):
            print('\n La firma digital no coincide con el hash')
            return
        print('OK')
        print('Fichero obtenido. Guardando fichero en disco...')
        filename = resp.headers['content-disposition'].split('\"')[-2]
        f = open(filename, 'wb')
        f.write(doc.content)
        print('Fichero con ID: ' + fileid + ' guardado correctamente con nombre: ' + filename)

def delete_file_routine(fileid):
    print('Borrando el archivo del servidor...', end='')
    url = build_url('filedelete')
    params = {'file_id':fileid}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    jresp = resp.json()
    if code == 200:
        print('OK')
        print('El fichero ' + jresp['file_id'] + ' ha sido borrado satisfactoriamente')

def code_checker(resp):
    if resp.status_code is 200:
        return 200
    else:
        json_resp = resp.json()
        print('\n Ha ocurrido un error. Código de error:')
        print(json_resp['error_code'], '\n')
        print(json_resp['description'], '\n')
        err_code = json_resp['error_code']
        print('Para más información visita: https://vega.ii.uam.es/2302-02-19/practica2/wiki/...') #TODO: Completar con la WIKI
        return err_code

def print_found_users(found):
    i=1
    for rec in found:
        print('['+str(i)+']', rec['nombre'], ',', rec['email'], ', ID:', rec['userID'])
        i+=1

def print_found_files(found):
    i=1
    for rec in found:
        print('['+str(i)+']', rec['fileID'], rec['fileName'])
        i+=1

def search_users_on_sv(string):
    params={'data_search':string}
    url = build_url('search')
    resp = req.post(url, json=params, headers=headers)
    return resp

def get_publicKey(user_id):
    url = build_url('getpk')
    params = {'userID':user_id}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    jresp = resp.json()
    return jresp['publicKey']
