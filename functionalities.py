import requests as req
from Crypto.PublicKey import RSA
import json
import os
import document_sign import *

api_url = 'http://vega.ii.uam.es:8080/api/'
headers = {'content-type': 'application/json', 'authorization': 'Bearer 5BCd38106c97FEbA'}
endpoints = {'create':'users/register', 'userdelete':'users/delete', 'search':'users/search',
              'getpk':'users/getPublicKey', 'up':'files/upload', 'dwn':'files/download',
               'list':'files/list', 'filedelete':'files/delete'}

def build_url(key):
    return api_url+endpoints[key]

def create_id_routine(name, email, alias=None): #alias sirve para algo?
    print('Generando par de claves RSA de 2048 bits...')

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
        found = search_on_sv(jresp['nombre'])
        if code_checker(found) is 200:
            jfound = found.json()
            for rec in jfound:
                if rec['nombre'] == jresp['nombre'] and rec['email'] == email and\
                   rec['publicKey'] == pkPEM:
                   print('Identidad con ID#' +  rec['userID'] + ' creada correctamente')
                   break
        #print(rsaKey.exportKey()) #TODO: Guardar clave privada en algun lado
        return rsaKey
    return None

def delete_id_routine(userID):
    print('Borrando usuario con ID#', userID, '...')
    params = {'userID':userID}
    url = build_url('userdelete')
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        print('OK')

def upload_routine(path, private_key):
    if os.path.isfile(path):
        url = build_url('up')
        headers = {'authorization': 'Bearer 5BCd38106c97FEbA'} #Quitamos el content-type json
        #Encrypt
        doc = docusign(path)
        doc.digital_sign(private_key)
        doc.cipher(private_key)
        doc.prepare_upload()
        #Send file
        files = {'ufile': (path, doc.ciphered)}
        resp = req.post(url, headers=headers, files=files)
        #TODO: Checkings
    else:
        print('La ruta proporcionada es incorrecta')


def search_id_routine(string):
    print('Buscando coincidencias con: <<', string,'>> en el servidor')
    params={'data_search':string}
    url = build_url('search')
    resp = search_on_sv(string)
    code = code_checker(resp)
    if code is 200:
        print('OK')
        return resp.json()
    return None

def list_files_routine():
    print('Obteniendo la lista de ficheros subidos...')
    url = build_url('list')
    resp = req.post(url, headers=headers)
    code = code_checker(resp)
    if code is 200:
        print('OK')
        return resp.json()
    return None

def download_routine(fileid):
    print('Obteniendo el fichero del servidor...')
    url = build_url('dwn')
    params = {'file_id':fileid}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        #TODO: Check signature and decrypt
        print('Fichero obtenido. Guardando fichero en disco...')
        f = open(fileid + '.txt', 'w+')
        f.write(resp.text)
        print('Fichero con ID: ' + fileid + ' guardado correctamente.')

def delete_file_routine(fileid):
    print('Borrando el archivo del servidor...')
    url = build_url('filedelete')
    params = {'file_id':fileid}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    jresp = resp.json()
    if code == 200:
        print('El fichero ' + jresp['file_id'] + ' ha sido borrado satisfactoriamente')

def code_checker(resp):
    if resp.status_code is 200:
        return 200
    else:
        json_resp = resp.json()
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

def search_on_sv(string):
    params={'data_search':string}
    url = build_url('search')
    resp = req.post(url, json=params, headers=headers)
    return resp
