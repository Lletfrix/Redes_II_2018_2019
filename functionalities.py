url = 'http://vega.ii.uam.es:8080/api/'
headers = {'content-type': 'application/json', 'authorization': 'Bearer 5BCd38106c97FEbA'}

def create_id_routine(name, email, alias=None): #alias sirve para algo?
    print('Generando par de claves RSA de 2048 bits...')
    #generate public key
    print('OK')
    params = {'nombre': name, 'email': email, 'publicKey': pk};
    full_url = url + 'users/register'
    resp = req.post(full_url, json=params, headers=headers)
    code = code_checker(resp)
    if code == 200:
        json_resp = resp.json()
        #id = json_resp[""]
        #print("Identidad con ID#", id, "creada correctamente") #ver como hacer esto

def delete_id_routine(userID):
    print('Borrando usuario con ID#', userID, "...")
    params = {'userID': userID}
    full_url = url + 'users/delete'
    resp = req.post(full_url, json=params, headers=headers)
    code = code_checker(resp)
    if code == 200:
        print("OK")

def code_checker(resp):
    if resp.status_code == 200:
        return 200
    else:
        json_resp = resp.json()
        print(json_resp['description'], '\n')
        err_code = json_resp['error_code']
        if err_code == 'TOK1':
            print('Comprueba que has escrito el token correctamente o solicita otro en la web')
        elif err_code == 'TOK2':
            print('Solicita un nuevo token en la web')
        elif err_code == 'TOK3':
            print('Comprueba que has incluido el header "Authorization: Bearer <Token>" en la petición')
        elif err_code == 'FILE1':
            print('Prueba con un fichero de tamaño inferior a 50 Kb')
        elif err_code == 'FILE2':
            print('Comprueba que el ID del fichero es correcto y que tienes permiso para acceder a él')
        elif err_code == 'FILE3':
            print('Borra algún fichero para poder subir otro')
        elif err_code == 'USER_ID1':
            print('Comprueba que el ID proporcionado es correcto')
        elif err_code == 'USER_ID2':
            print('Comprueba que has escrito bien el criterio de búsqueda')
        elif err_code == 'ARGS1':
            print('Comprueba la petición HTTP')
        return err_code
