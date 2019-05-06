import requests as req
from Crypto.PublicKey import RSA
import json
import os
from document_sign import *

#Macros
api_url = 'http://vega.ii.uam.es:8080/api/' #Url de la api a utilizar
headers = {'content-type': 'application/json', 'authorization': None}   #Headers de las peticiones
endpoints = {'create':'users/register', 'userdelete':'users/delete', 'search':'users/search',
              'getpk':'users/getPublicKey', 'up':'files/upload', 'dwn':'files/download',
               'list':'files/list', 'filedelete':'files/delete'}    #Diccionario de endpoints
up_route = 'Uploads/'
down_route = 'Downloads/'   #Carpetas de organización de ficheros

# Función que construye la url completa para cierto endpoint
# input key Identificador del endpoint en nuestro diccionario
# output url completa
def build_url(key):
    return api_url+endpoints[key]

# Función que registra una identidad en el servidor
# input name Nick del usuario, email Email del usuario
# output clave privada, None si hay error
def create_id_routine(name, email):
    print('Generando par de claves RSA de 2048 bits...', end='')
    rsaKey = RSA.generate(2048)
    pkPEM = rsaKey.publickey().exportKey().decode('ascii')
    print('OK') #Clave generada en formato pem

    # Petición de registro al servidor en JSON
    params = {'nombre': name, 'email': email, 'publicKey': pkPEM}
    url = build_url('create')
    resp = req.post(url, json=params, headers=headers)

    code = code_checker(resp)   #Comprobamos el código de la respuesta
    if code is 200:
        jresp = resp.json()
        found = search_users_on_sv(jresp['nombre']) #Si es 200, buscamos la identidad creada para devolver el ID
        if code_checker(found) is 200:
            jfound = found.json()
            for rec in jfound:
                if rec['nombre'] == jresp['nombre'] and rec['email'] == email and\
                   rec['publicKey'] == pkPEM:
                   print('Identidad con ID#' +  rec['userID'] + ' creada correctamente')
                   break
        return rsaKey   #Si nos encontramos, informamos del éxito del registro y devolvemos la clave generada
    return None #Si hay error no devolvemos nada

# Función que borra una identidad del servidor
# input userID id del user a eliminar
# Aclaración: Como el servidor nos devuelve 200 tanto si se ha borrado como
# si no, no podemos saber si el borrado ha sido efectivo
def delete_id_routine(userID):
    print('Borrando usuario con ID#', userID, '...', end='')
    params = {'userID':userID}
    url = build_url('userdelete')
    resp = req.post(url, json=params, headers=headers)  #Construimos y enviamos la petición al servidor
    code = code_checker(resp)   #Comprobamos el código de respuesta
    if code is 200:
        print('OK')

# Función que firma y cifra un fichero y lo sube al servidor
# input path Nombre del fichero, private_key Clave privada, public_key Clave pública
def upload_routine(path, private_key, public_key):
    abspath = up_route+path #Construimos la ruta absoluta del fichero
    if os.path.isfile(abspath): #Comprobamos si es un fichero
        url = build_url('up')   #Construimos la url de upload
        up_headers = dict(headers)
        up_headers.pop('content-type') #Quitamos el content-type JSON de los headers por defecto
        #Obtenemos el fichero y creamos un docusign que lo contendrá
        print('Obteniendo fichero...', end='')
        doc = docusign(abspath)
        print('OK')
        #Firmamos
        print('Generando firma digital...', end='')
        doc.get_digital_sign(private_key)
        print('OK')
        #Ciframos
        print('Cifrando fichero...', end='')
        doc.cipher(private_key)
        print('OK')
        #Generamos sobre digital
        print('Generando sobre digital...', end='')
        doc.get_digital_envelope(public_key)
        print('OK')
        print('Subiendo fichero...', end='')
        doc.prepare_upload()
        #Enviamos el fichero al servidor
        files = {'ufile': (path, doc.ciphered)}
        resp = req.post(url, headers=up_headers, files=files)
        code = code_checker(resp)   #Comprobamos el código de respuesta
        if code is 200:
            print('OK')
            file_id = resp.json()['file_id']
            print('Subida realizada correctamente, ID del fichero:', file_id)
    else:
        print('La ruta proporcionada es incorrecta')

# Función que busca usuarios en el servidor dada una string
# input string String a buscar en los campos de los usuarios
# output lista de usuarios, None si ha habido error
def search_id_routine(string):
    print('Buscando coincidencias con: <<', string,'>> en el servidor')
    resp = search_users_on_sv(string)   #Obtenemos la respuesta del servidor
    code = code_checker(resp)   #Comprobamos la respuesta
    if code is 200:
        print('OK')
        return resp.json()  #Devolvemos los usuarios encontrados
    return None #Si hay error no devolvemos nada

# Función que obtiene la lista de ficheros de un usuario
# output lista de ficheros, None si hay error
def list_files_routine():
    print('Obteniendo la lista de ficheros subidos...', end='')
    url = build_url('list') #Construimos la url
    resp = req.post(url, headers=headers)
    code = code_checker(resp)   #Comprobamos el código de respuesta
    if code is 200:
        print('OK')
        return resp.json()  #Devolvemos la información de los ficheros
    return None #Si hay error no devolvemos nada

# Función que descarga un fichero del servidor
# input fileid ID del fichero a descargar, private_key Clave privada, public_key Clave pública
def download_routine(fileid, private_key, public_key):
    print('Obteniendo el fichero del servidor...', end='')
    url = build_url('dwn')
    params = {'file_id':fileid}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        #Desciframos
        doc = docusign(None, resp.content)
        doc.get_session_key(private_key)
        doc.decipher()
        #Comprobamos la firma digital
        if not doc.verify_signature(public_key):
            print('\n La firma digital no coincide con el hash')
            return
        print('OK')
        #Guardamos el fichero en la carpeta de descargas con su nombre
        print('Fichero obtenido. Guardando fichero en disco...')
        filename = resp.headers['content-disposition'].split('\"')[-2]  #Obtenemos el nombre original del fichero
        fileroute = down_route+filename
        f = open(fileroute, 'wb')
        f.write(doc.content)
        print('Fichero con ID: ' + fileid + ' guardado correctamente con nombre: ' + filename)

# Función que borra un fichero del servidor
# input fileid ID del fichero a borrar
def delete_file_routine(fileid):
    print('Borrando el archivo del servidor...', end='')
    url = build_url('filedelete')
    params = {'file_id':fileid} #Construimos la petición
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)   #Comprobamos el código de respuesta
    if code == 200:
        jresp = resp.json()
        print('OK')
        print('El fichero ' + jresp['file_id'] + ' ha sido borrado satisfactoriamente')

# Función que devuelve el código de respuesta. Además, si no es 200 imprime el código
# y una pequeña descripción ampliable por la wiki
# input resp Respuesta del servidor
# output 200 o código de error
def code_checker(resp):
    if resp.status_code is 200:
        return 200
    else:
        json_resp = resp.json() #Obtenemos los detalles del error
        print('\n Ha ocurrido un error. Código de error:')
        print(json_resp['error_code'], '\n')
        print(json_resp['description'], '\n')
        err_code = json_resp['error_code']
        print('Para más información visita: https://vega.ii.uam.es/2302-02-19/practica2/wikis/errores')
        return err_code

# Función que imprime por pantalla los usuarios encontrados dados por entrada
# input found Lista de usuarios encontrados
def print_found_users(found):
    i=1
    for rec in found:
        print('['+str(i)+']', rec['nombre'], ',', rec['email'], ', ID:', rec['userID'])
        i+=1

# Función que imprime por pantalla los ficheros encontrados dados por entrada
# input found Lista de ficheros encontrados
def print_found_files(found):
    i=1
    for rec in found:
        print('['+str(i)+']', rec['fileID'], rec['fileName'])
        i+=1

# Función que busca usuarios cuyos campos contengan una string dada
# input string String a buscar en los campos
# output respuesta del servidor
def search_users_on_sv(string):
    params={'data_search':string}
    url = build_url('search')
    resp = req.post(url, json=params, headers=headers)
    return resp

# Función que obtiene la clave pública de un usuario
# input user_id ID del usuario del que se quiere la clave
# output clave pública del usuario
def get_publicKey(user_id):
    url = build_url('getpk')
    params = {'userID':user_id}
    resp = req.post(url, json=params, headers=headers)
    code = code_checker(resp)
    if code is 200:
        jresp = resp.json()
        return jresp['publicKey']
    return None

# Función que cifra un fichero para almacenarlo en local
# input path Ruta del fichero, private_key Clave privada, public_key Clave pública
def encrypt_routine(path, private_key, public_key):
    doc = docusign(path)
    doc.encrypt(public_key) #Ciframos el fichero
    doc.get_digital_envelope(private_key)
    f = open(path+'.enc', 'wb')
    f.write(doc.iv+doc.digital_envelope+doc.ciphered)   #Guardamos el fichero cifrado

# Función que firma un fichero para almacenarlo en local
# input path Ruta del fichero, private_key Clave privada
def sign_routine(path, private_key):
    doc = docusign(path)
    doc.get_digital_sign(private_key)   # Firmamos el fichero
    f = open(path+'.sgn', 'wb')
    f.write(doc.digital_sign+doc.content)   #Guardamos el fichero

# Función que cifra y firma un fichero para almacenarlo en local
# input path Ruta del fichero, private_key Clave privada, public_key Clave pública
def enc_sign_routine(path, private_key, public_key):
    print('Obteniendo fichero...', end='')
    doc = docusign(path)
    print('OK')
    #Firmado
    print('Generando firma digital...', end='')
    doc.get_digital_sign(private_key)
    print('OK')
    #Cifrado
    print('Cifrando fichero...', end='')
    doc.cipher(private_key)
    print('OK')
    #Generación de sobre digital
    print('Generando sobre digital...', end='')
    doc.get_digital_envelope(public_key)
    print('OK')
    #Guardamos fichero
    print('Escribiendo fichero...', end='')
    doc.prepare_upload()
    f = open(path+'.enc.sgn', 'wb')
    f.write(doc.ciphered)
