from math import sqrt

def pts(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo):
    if tempo > 0 and popularidad > 0:
        media_armonica = 2 / ((1 / tempo) + (1 / popularidad))
    else:
        media_armonica = 0.0

    factor_intensidad = (avatars_matados / (tempo + 1)) * 0.05

    factor_avatar = 1 + sqrt(puntos_avatar / 500)

    puntaje_ajustado = (media_armonica + (factor_intensidad * 100)) * factor_avatar

    if puntaje_ajustado > limite_maximo:
        puntaje_ajustado = limite_maximo

    return puntaje_ajustado