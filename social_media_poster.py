# social_media_poster.py (SOLO INSTAGRAM - TOP 10)
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
from datetime import datetime
import time

try:
    from config import *
except ImportError:
    INSTAGRAM_USERNAME = ""
    INSTAGRAM_PASSWORD = ""


class SocialMediaPoster:
    def __init__(self):
        self.instagram_client = None
        
    def crear_imagen_ranking(self, usuarios_top):
        """Crea imagen optimizada para Instagram (1080x1350) - TOP 10"""
        width, height = 1080, 1350  # Altura aumentada para 10 usuarios
        color_primario = (138, 28, 50)
        
        img = Image.new('RGB', (width, height), color=color_primario)
        draw = ImageDraw.Draw(img)
        
        # Gradiente de fondo
        for i in range(height):
            ratio = i / height
            r = int(138 + (97 - 138) * ratio)
            g = int(28 + (20 - 28) * ratio)
            b = int(50 + (35 - 50) * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Cargar fuentes
        try:
            font_title = ImageFont.truetype("arial.ttf", 50)
            font_name = ImageFont.truetype("arialbd.ttf", 32)
            font_pts = ImageFont.truetype("arial.ttf", 26)
        except:
            font_title = ImageFont.load_default()
            font_name = font_title
            font_pts = font_title
        
        y_pos = 30
        
        # Logo si existe
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Logo.jpg")
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert('RGB')
                logo_size = 100
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                
                # Hacer circular el logo
                mask = Image.new('L', (logo_size, logo_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)
                
                output = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
                output.paste(logo, (0, 0))
                output.putalpha(mask)
                
                img.paste(output, (width//2 - logo_size//2, y_pos), output)
                y_pos += logo_size + 15
        except Exception as e:
            print(f"   ⚠️ No se pudo cargar logo: {e}")
        
        # Título
        titulo = "🏆 SALÓN DE LA FAMA 🏆"
        bbox = draw.textbbox((0, 0), titulo, font=font_title)
        text_width = bbox[2] - bbox[0]
        draw.text((width//2 - text_width//2, y_pos), titulo, 
                 fill='white', font=font_title)
        y_pos += 60
        
        # Top 10 usuarios
        medals = {
            1: ("🥇", (255, 215, 0)), 
            2: ("🥈", (192, 192, 192)), 
            3: ("🥉", (205, 127, 50))
        }
        
        for i, (username, datos) in enumerate(usuarios_top[:10], 1):  # TOP 10
            nombre = f"{datos.get('nombre', '')} {datos.get('apellido', '')}"
            pts = datos.get('pts', 0)
            
            medal, medal_color = medals.get(i, (f"{i}.", (180, 180, 180)))
            
            # Fondo (más compacto para caber 10)
            rect_height = 62
            draw.rounded_rectangle(
                [(40, y_pos), (width - 40, y_pos + rect_height)],
                radius=10,
                fill=tuple([int(c * 0.3) for c in medal_color]),
                outline=medal_color,
                width=2
            )
            
            # Medalla/Número
            if i <= 3:
                draw.text((60, y_pos + 8), medal, fill='white', font=font_title)
            else:
                draw.text((65, y_pos + 15), f"{i}.", fill='white', font=font_name)
            
            # Nombre
            draw.text((130, y_pos + 8), nombre, fill='white', font=font_name)
            
            # Puntos
            pts_text = f"{pts} pts"
            bbox = draw.textbbox((0, 0), pts_text, font=font_pts)
            pts_width = bbox[2] - bbox[0]
            draw.text((width - 110 - pts_width, y_pos + 18), pts_text, 
                     fill=medal_color, font=font_pts)
            
            y_pos += rect_height + 12
        
        # Fecha
        fecha = datetime.now().strftime('%d/%m/%Y')
        draw.text((width//2 - 60, height - 35), f"🎮 {fecha}", 
                 fill=(200, 200, 200), font=font_pts)
        
        return img
    
    def publicar_instagram(self, usuarios_top, caption_personalizado=None):
        """Publica en Instagram con imagen"""
        try:
            print("📸 Publicando en Instagram...")
            
            # Login
            if not self.instagram_client:
                self.instagram_client = Client()
                
                # Intentar cargar sesión guardada
                try:
                    self.instagram_client.load_settings("instagram_session.json")
                    print("   📂 Usando sesión guardada...")
                except:
                    print("   🔐 Creando nueva sesión...")
                    time.sleep(2)
                
                self.instagram_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                
                # Guardar sesión
                try:
                    self.instagram_client.dump_settings("instagram_session.json")
                except:
                    pass
            
            # Crear imagen
            img = self.crear_imagen_ranking(usuarios_top)
            
            # Guardar temporalmente
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=95)
            temp_file.close()
            
            # Caption
            if caption_personalizado:
                caption = caption_personalizado
            else:
                caption = "🏆 ¡Ranking Actualizado! 🏆\n\n"
                caption += "Top 10 jugadores de Avatars VS Rooks:\n\n"
                
                for i, (username, datos) in enumerate(usuarios_top[:10], 1):  # TOP 10
                    nombre = f"{datos.get('nombre', '')} {datos.get('apellido', '')}"
                    pts = datos.get('pts', 0)
                    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                    medal = medals.get(i, f"{i}.")
                    caption += f"{medal} {nombre} - {pts} pts\n"
                
                caption += "\n#AvatarsVSRooks #Gaming #TowerDefense #IndieGame "
                caption += "#CostaRica #GameDev #TEC"
            
            # Subir
            media = self.instagram_client.photo_upload(temp_file.name, caption)
            os.unlink(temp_file.name)
            
            print(f"   ✅ Post publicado (ID: {media.pk})")
            print(f"   🔗 Ver: https://www.instagram.com/p/{media.code}/")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def publicar(self, usuarios_top, mensaje=None):
        """Publica en Instagram"""
        print("\n" + "=" * 60)
        print("📢 PUBLICANDO RANKING EN INSTAGRAM")
        print("=" * 60 + "\n")
        
        resultado = self.publicar_instagram(usuarios_top, mensaje)
        
        print("\n" + "=" * 60)
        if resultado:
            print("✅ ÉXITO: Ranking publicado en Instagram")
        else:
            print("❌ FALLÓ: No se pudo publicar en Instagram")
        print("=" * 60 + "\n")
        
        return resultado


# Test
if __name__ == "__main__":
    print("🧪 MODO DE PRUEBA - INSTAGRAM (TOP 10)\n")
    
    usuarios_prueba = [
        ("adriel", {"nombre": "Adriel", "apellido": "Castro", "pts": 2500}),
        ("maria_gamer", {"nombre": "María", "apellido": "López", "pts": 2100}),
        ("carlos_pro", {"nombre": "Carlos", "apellido": "Ruiz", "pts": 1800}),
        ("ana_player", {"nombre": "Ana", "apellido": "Mora", "pts": 1500}),
        ("luis99", {"nombre": "Luis", "apellido": "Rojas", "pts": 1200}),
        ("pepe_gamer", {"nombre": "Pepe", "apellido": "Vega", "pts": 1100}),
        ("sofia_pro", {"nombre": "Sofía", "apellido": "Díaz", "pts": 1000}),
        ("juan_player", {"nombre": "Juan", "apellido": "Ramírez", "pts": 950}),
        ("laura_gamer", {"nombre": "Laura", "apellido": "Torres", "pts": 900}),
        ("diego_pro", {"nombre": "Diego", "apellido": "Castro", "pts": 850}),
    ]
    
    poster = SocialMediaPoster()
    poster.publicar(usuarios_prueba)