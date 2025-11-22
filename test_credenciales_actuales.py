# test_instagram.py
from config import *
from instagrapi import Client

print("=" * 60)
print("📸 PROBANDO INSTAGRAM")
print("=" * 60)

print(f"\nUsername: {INSTAGRAM_USERNAME}")
print(f"Password: {'*' * len(INSTAGRAM_PASSWORD)}")

try:
    print("\n🔐 Intentando login...")
    cl = Client()
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    
    print("✅ LOGIN EXITOSO!")
    
    user_info = cl.user_info(cl.user_id)
    print(f"\n📱 Info de tu cuenta:")
    print(f"   Username: @{user_info.username}")
    print(f"   Nombre: {user_info.full_name}")
    print(f"   Seguidores: {user_info.follower_count}")
    print(f"   Posts: {user_info.media_count}")
    
    respuesta = input("\n¿Publicar foto de prueba del ranking? (s/n): ")
    
    if respuesta.lower() == 's':
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        import os
        
        # Crear imagen simple de prueba
        img = Image.new('RGB', (1080, 1080), color=(138, 28, 50))
        draw = ImageDraw.Draw(img)
        
        # Título
        try:
            font_big = ImageFont.truetype("arial.ttf", 80)
            font_small = ImageFont.truetype("arial.ttf", 40)
        except:
            font_big = ImageFont.load_default()
            font_small = font_big
        
        draw.text((540, 400), "🏆 Avatars VS Rooks 🏆", 
                 fill='white', font=font_big, anchor='mm')
        draw.text((540, 500), "Ranking Bot Test", 
                 fill='white', font=font_small, anchor='mm')
        
        # Guardar temporalmente
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG', quality=95)
        temp_file.close()
        
        # Publicar
        caption = "🎮 ¡Probando el bot de Avatars VS Rooks! 🏆\n\n#AvatarsVSRooks #Gaming #TowerDefense #IndieGame"
        media = cl.photo_upload(temp_file.name, caption)
        
        print(f"\n✅ ¡Foto publicada en Instagram!")
        print(f"   URL: https://www.instagram.com/p/{media.code}/")
        print(f"   Ve a tu perfil: https://www.instagram.com/{INSTAGRAM_USERNAME}/")
        
        os.unlink(temp_file.name)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Posibles causas:")
    print("   1. Password incorrecta")
    print("   2. Instagram bloqueó el login (prueba más tarde)")
    print("   3. 2FA activado (desactívalo en la app)")

print("\n" + "=" * 60)