# leer_popularidad.py
from ventana_personalizacion import get_popularidad

p = get_popularidad()  # imprime y retorna
if p is not None:
    # si quieres hacer algo con el valor:
    print("Valor devuelto:", int(p))
