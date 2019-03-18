import requests as req
from Crypto.PublicKey import RSA
import json

url = 'http://vega.ii.uam.es:8080/api/'
headers = {'content-type': 'application/json', 'authorization': 'Bearer 5BCd38106c97FEbA'}

def create_id_routine(name, email, alias=None): #alias sirve para algo?
    print('Generando par de claves RSA de 2048 bits...')

    rsaKey = RSA.generate(2048)
    pkPEM = rsaKey.publickey().exportKey().decode('ascii') #Get pem format

    totalName = name+'#'+alias if alias else name #Concatenate alias if available
    print('OK')

    params = {"nombre": totalName, "email": email, "publicKey": pkPEM}
    full_url = url + 'users/register'
    resp = req.post(full_url, json=params, headers=headers)
    
    code = code_checker(resp)
    if code is 200:
        json_resp = resp.json()
        print(json_resp)
        #id = json_resp[""]
        #print("Identidad con ID#", id, "creada correctamente") #ver como hacer esto
        print(rsaKey.exportKey())
        return rsaKey
    return None

def delete_id_routine(userID):
    print('Borrando usuario con ID#', userID, "...")
    params = {'userID': userID}
    full_url = url + 'users/delete'
    resp = req.post(full_url, json=params, headers=headers)
    code = code_checker(resp)
    if code == 200:
        print("OK")

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
