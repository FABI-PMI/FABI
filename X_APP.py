import tweepy
from Login import cargar_usuarios

# Configuración de las credenciales de la API de Twitter
#API_KEY = "2oziyvLOBpu7qZboheXOXliDp"
#API_SECRET = "WSTHOh5qVFJuay7KfLnwIV3AQV6VYv6lSBnNrktUAtxJOZ51Zd"
#ACCESS_TOKEN = "1992346552179081216-Ac3Tau01bS0Gn72kgm67N9zIsHzAkC"
#ACCESS_SECRET = "EA3jj6kljxfyxnCJRL68ZODHp0oTO5rdLYHaNAbGq7FeQ"

# Credenciales de la API de Twitter para pruebas
API_KEY = "TiYrS7LGxJW7f66zfYEbQApPa"
API_SECRET = "6qRgBp8CZKvWPjGaGmIm00hUU9jijwN1M5qtrYyHFMXdA7Cd5d"
ACCESS_TOKEN = "1992411524678443008-N80qzdpim2jPc5thBWFvTzoFW4Mt1P"
ACCESS_SECRET = "BJsD6GwQdq6IsxssPcACLq2wK29fYuyQDv2rZ2PTWQzpk"

def obtener_top_usuarios():
    """Obtiene el top 8 de usuarios ordenados por puntos"""
    usuarios = cargar_usuarios()
    usuarios_con_pts = []
    
    for username, datos in usuarios.items():
        if isinstance(datos, dict):
            pts = datos.get('pts', 0)
            nombre_completo = f"{datos.get('nombre', '')} {datos.get('apellido', '')}"
            usuarios_con_pts.append((nombre_completo.strip(), pts))
    
    # Ordenar por puntos (mayor a menor)
    usuarios_con_pts.sort(key=lambda x: x[1], reverse=True)
    
    # Retornar solo top 8
    return usuarios_con_pts[:8]

def crear_texto_tweet():
    """Crea el texto del tweet con el ranking actual - TOP 8 COMPACTO"""
    top_usuarios = obtener_top_usuarios()
    
    if not top_usuarios:
        return "🏆 SALÓN DE LA FAMA\n\nNo hay usuarios registrados aún."
    
    texto = "🏆 SALÓN DE LA FAMA\n\n"
    
    for i, (nombre, pts) in enumerate(top_usuarios, 1):
        # Emojis especiales para top 3
        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = f"{i}."
        
        # Truncar nombre si es muy largo (máximo 15 caracteres)
        nombre_corto = nombre[:15] if len(nombre) > 15 else nombre
        
        # Formato compacto: emoji nombre - puntos
        texto += f"{emoji} {nombre_corto} - {pts}\n"
    
    texto += "\n#AvatarsVSRooks"
    
    return texto

def publicar_ranking_twitter():
    """Publica el ranking actual en Twitter"""
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, 
        access_token_secret=ACCESS_SECRET
    )
    
    try:
        texto_tweet = crear_texto_tweet()
        resp = client.create_tweet(text=texto_tweet)
        print("✅ Tweet enviado con éxito!")
        print(f"ID del tweet: {resp.data['id']}")
        print("\nContenido publicado:")
        print("-" * 40)
        print(texto_tweet)
        print("-" * 40)
        return True
    except Exception as e:
        print(f"❌ Error al enviar el tweet: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🐦 Publicando ranking en Twitter/X...")
    print("=" * 50)
    publicar_ranking_twitter()