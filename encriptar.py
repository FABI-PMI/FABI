from cryptography.fernet import Fernet
import json

ARCHIVO_ENTRADA = 'usuarios.json'
ARCHIVO_SALIDA = 'usuarios.json.enc'
ARCHIVO_CLAVE = 'clave.key'

def generar_clave():
    clave = Fernet.generate_key()
    with open(ARCHIVO_CLAVE, 'wb') as archivo:
        archivo.write(clave)
    print(f'Clave generada y guardada en: {ARCHIVO_CLAVE}')
    return clave

def cargar_clave():
    with open(ARCHIVO_CLAVE, 'rb') as archivo:
        return archivo.read()

def encriptar():
    try:
        clave = cargar_clave()
        print('Clave cargada')
    except FileNotFoundError:
        clave = generar_clave()
    
    with open(ARCHIVO_ENTRADA, 'r', encoding='utf-8') as archivo:
        datos = archivo.read()
    
    fernet = Fernet(clave)
    datos_encriptados = fernet.encrypt(datos.encode())
    
    with open(ARCHIVO_SALIDA, 'wb') as archivo:
        archivo.write(datos_encriptados)
    
    print(f'Archivo encriptado en: {ARCHIVO_SALIDA}')

def desencriptar():
    clave = cargar_clave()
    
    with open(ARCHIVO_SALIDA, 'rb') as archivo:
        datos_encriptados = archivo.read()
    
    fernet = Fernet(clave)
    datos_desencriptados = fernet.decrypt(datos_encriptados)
    
    print('Contenido desencriptado:')
    print(datos_desencriptados.decode('utf-8'))

if __name__ == '__main__':
    encriptar()
