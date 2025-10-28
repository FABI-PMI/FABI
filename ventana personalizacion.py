"""
Ventana de personalización con preview del juego en tiempo real.
Versión mejorada sin playsound (solo VLC y pygame)
"""
import tkinter as tk
from tkinter import messagebox
import math
import sys
import os

# Configuración de rutas para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Intentar importar módulos del juego
try:
    from PaletaColores import generate_palette
    from VentanaPrincipal import VillageGame
    GAME_AVAILABLE = True
except ImportError as e:
    GAME_AVAILABLE = False

# Intentar importar módulos de música
try:
    from yt_dlp import YoutubeDL
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

# Sistema mejorado de detección de reproductores (SIN PLAYSOUND)
AUDIO_PLAYER = None
VLC_ERROR = None
PYGAME_ERROR = None

# Intentar VLC primero
try:
    import os
    import sys
    
    # Agregar rutas comunes de VLC en Windows
    vlc_paths = [
        r'C:\Program Files\VideoLAN\VLC',
        r'C:\Program Files (x86)\VideoLAN\VLC',
    ]
    
    # Agregar la ruta de VLC al PATH si existe
    vlc_found = False
    for vlc_path in vlc_paths:
        if os.path.exists(vlc_path):
            os.environ['PATH'] = vlc_path + ';' + os.environ.get('PATH', '')
            print(f"✓ VLC encontrado en: {vlc_path}")
            vlc_found = True
            break
    
    if not vlc_found:
        print("⚠ VLC no encontrado en rutas por defecto")
    
    # Intentar importar el módulo VLC
    import vlc
    
    # Verificar que VLC funcione creando una instancia de prueba
    test_instance = vlc.Instance('--no-video', '--quiet')
    test_player = test_instance.media_player_new()
    
    AUDIO_PLAYER = 'vlc'
    print("✓ VLC detectado y funcionando correctamente")
    
except Exception as e:
    VLC_ERROR = str(e)
    print(f"✗ VLC no disponible: {e}")
    AUDIO_PLAYER = None

# Si VLC falla, intentar pygame
if AUDIO_PLAYER is None:
    try:
        from pygame import mixer
        # Probar inicializar pygame
        mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        mixer.quit()  # Cerrar por ahora, se reiniciará después
        
        AUDIO_PLAYER = 'pygame'
        print("✓ pygame detectado y funcionando")
    except Exception as e:
        PYGAME_ERROR = str(e)
        print(f"✗ pygame no disponible: {e}")
        AUDIO_PLAYER = None

# Si ninguno funciona, mostrar advertencia
if AUDIO_PLAYER is None:
    print("=" * 60)
    print("⚠ ADVERTENCIA: No hay reproductor de audio disponible")
    print("=" * 60)
    print("\nPara habilitar la reproducción de música, instala:")
    print("1. VLC Media Player: https://www.videolan.org/vlc/")
    print("   O")
    print("2. pygame: pip install pygame")
    print("=" * 60)

import tempfile
import os as os_module
import threading


class ColorSelectorApp:
    """
    Aplicación principal de personalización del juego.
    Permite seleccionar color favorito, tema y música, con preview en tiempo real.
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana de personalización.
        
        Args:
            root: Ventana principal de Tkinter
        """
        # Configuración de la ventana principal
        self.root = root
        self.root.title("Personalización - Sistema de Aldeas")
        
        # ==================== SISTEMA DE CENTRADO DE VENTANA ====================
        # Obtener el tamaño de la pantalla
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Definir tamaño de la ventana
        window_width = 1250  # Aumentado para acomodar preview más ancho
        window_height = 850  # Aumentado para acomodar preview más alto
        
        # Calcular la posición para centrar la ventana
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)
        
        # Establecer geometría y posición centrada
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.root.resizable(False, False)
        
        # Color de fondo fijo para toda la aplicación
        self.color_fondo_fijo = '#8a1c32'
        self.root.configure(bg=self.color_fondo_fijo)
        
        # Contenedor principal
        main_container = tk.Frame(root, bg=self.color_fondo_fijo)
        main_container.pack(fill='both', expand=True)
        
        # Crear paneles izquierdo (controles) y derecho (preview)
        self._crear_panel_izquierdo(main_container)
        self._crear_panel_preview(main_container)
        
        # Variables para control de música
        self.music_thread = None
        self.current_song_file = None
        self.is_playing = False
        self.is_paused = False
        self.vlc_player = None
        self.vlc_instance = None
        
        # Inicializar reproductor según disponibilidad
        if AUDIO_PLAYER == 'pygame':
            from pygame import mixer
            mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✓ pygame inicializado")
        elif AUDIO_PLAYER == 'vlc':
            import vlc
            self.vlc_instance = vlc.Instance('--no-video', '--quiet')
            print("✓ VLC inicializado")
        
        # Aplicar tema inicial
        self.cambiar_tema()
        
        # Actualizar paleta del preview si está disponible
        if GAME_AVAILABLE and self.game_preview:
            self.update_game_palette()
    
    def _crear_panel_izquierdo(self, parent):
        """Crea el panel izquierdo con todos los controles de personalización."""
        left_panel = tk.Frame(parent, bg=self.color_fondo_fijo, width=600)
        left_panel.pack(side='left', fill='both', expand=False, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        left_canvas = tk.Canvas(left_panel, bg=self.color_fondo_fijo, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
        self.scrollable_frame = tk.Frame(left_canvas, bg=self.color_fondo_fijo)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        left_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)
        
        left_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.main_canvas = left_canvas
        
        self.color_favorito = tk.StringVar(value="#a4244d")
        self.tema_var = tk.StringVar(value="claro")
        self.cancion_var = tk.StringVar()
        
        self.tema_var.trace('w', self.cambiar_tema)
        
        self._crear_titulo()
        self._crear_seccion_color()
        self._crear_seccion_tema()
        self._crear_seccion_musica()
        
        self.espacio_label = tk.Label(self.scrollable_frame, text="", bg=self.color_fondo_fijo)
        self.espacio_label.pack(pady=10)
    
    def _crear_titulo(self):
        """Crea el título principal de la ventana"""
        self.title_label = tk.Label(
            self.scrollable_frame, 
            text="PERSONALIZACIÓN", 
            font=("Arial", 28, "bold"), 
            bg=self.color_fondo_fijo, 
            fg='#ffffff'
        )
        self.title_label.pack(pady=20)
    
    def _crear_seccion_color(self):
        """Crea la sección de selección de color favorito."""
        self.color_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Seleccione su color favorito",
            font=("Arial", 13, "bold"), 
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20, 
            relief="groove", 
            bd=3
        )
        self.color_frame.pack(pady=10, padx=30, fill='x')
        
        self.canvas_color = tk.Canvas(
            self.color_frame, 
            width=220, 
            height=220, 
            bg='#ffffff', 
            highlightthickness=0
        )
        self.canvas_color.pack(pady=10)
        
        self.dibujar_rueda_color()
        self.canvas_color.bind("<Button-1>", self.seleccionar_color_rueda)
        
        self.color_info_frame = tk.Frame(self.color_frame, bg='#ffffff')
        self.color_info_frame.pack(pady=10)
        
        self.color_info_label = tk.Label(
            self.color_info_frame, 
            text="Color:", 
            font=("Arial", 10), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.color_info_label.pack(side='left', padx=5)
        
        self.color_display = tk.Canvas(
            self.color_info_frame, 
            width=60, 
            height=25, 
            bg=self.color_favorito.get(), 
            highlightthickness=2, 
            highlightbackground='#34495e'
        )
        self.color_display.pack(side='left', padx=5)
        
        self.color_label = tk.Label(
            self.color_info_frame, 
            text=self.color_favorito.get(), 
            font=("Arial", 10, "bold"), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.color_label.pack(side='left', padx=5)
    
    def _crear_seccion_tema(self):
        """Crea la sección de selección de tema."""
        self.tema_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Tema", 
            font=("Arial", 13, "bold"),
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20,
            relief="groove", 
            bd=3
        )
        self.tema_frame.pack(pady=10, padx=30, fill='x')
        
        self.opciones_frame = tk.Frame(self.tema_frame, bg='#ffffff')
        self.opciones_frame.pack()
        
        self.rb_oscuro = tk.Radiobutton(
            self.opciones_frame, 
            text="Oscuro", 
            variable=self.tema_var,
            value="oscuro", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_oscuro.grid(row=0, column=0, padx=25, pady=5)
        
        self.rb_claro = tk.Radiobutton(
            self.opciones_frame, 
            text="Claro", 
            variable=self.tema_var,
            value="claro", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_claro.grid(row=0, column=1, padx=25, pady=5)
        
        self.rb_medio = tk.Radiobutton(
            self.opciones_frame, 
            text="Término medio", 
            variable=self.tema_var,
            value="medio", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_medio.grid(row=0, column=2, padx=25, pady=5)
    
    def _crear_seccion_musica(self):
        """Crea la sección de música."""
        self.musica_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Música", 
            font=("Arial", 13, "bold"),
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20,
            relief="groove", 
            bd=3
        )
        self.musica_frame.pack(pady=10, padx=30, fill='x')
        
        self.musica_label = tk.Label(
            self.musica_frame, 
            text="Nombre de la canción:",
            font=("Arial", 11), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.musica_label.pack(anchor='w', pady=(5, 2))
        
        self.entry_cancion = tk.Entry(
            self.musica_frame, 
            textvariable=self.cancion_var,
            font=("Arial", 12), 
            width=40, 
            relief="solid", 
            bd=2
        )
        self.entry_cancion.pack(pady=(0, 15), ipady=5)
        
        self.botones_frame = tk.Frame(self.musica_frame, bg='#ffffff')
        self.botones_frame.pack()
        
        self.btn_buscar = tk.Button(
            self.botones_frame, 
            text="Buscar Canción",
            bg='#9b59b6', 
            fg='white', 
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=10, 
            command=self.buscar_cancion,
            cursor="hand2", 
            relief="raised", 
            bd=3, 
            width=18
        )
        self.btn_buscar.pack(pady=8)
        
        # Botón para pausar/reanudar música
        self.btn_pausar = tk.Button(
            self.botones_frame, 
            text="Pausar Música",
            bg='#3498db', 
            fg='white', 
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=10, 
            command=self.pausar_reanudar_musica,
            cursor="hand2", 
            relief="raised", 
            bd=3, 
            width=18,
            state='disabled'  # Deshabilitado al inicio
        )
        self.btn_pausar.pack(pady=8)
        
        self.btn_iniciar = tk.Button(
            self.botones_frame, 
            text="Avanzar",
            bg='#e74c3c', 
            fg='white', 
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=10, 
            command=self.iniciar_juego,
            cursor="hand2", 
            relief="raised", 
            bd=3, 
            width=18
        )
        self.btn_iniciar.pack(pady=8)
    
    def dibujar_rueda_color(self):
        """Dibuja una rueda de color interactiva tipo Paint."""
        center_x, center_y = 110, 110
        radius = 90
        num_segments = 360
        
        for i in range(num_segments):
            angle = i * (360 / num_segments)
            hue = angle / 360
            
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color = '#%02x%02x%02x' % rgb
            
            angle_rad = math.radians(angle)
            
            x1 = center_x + radius * math.cos(angle_rad)
            y1 = center_y + radius * math.sin(angle_rad)
            
            self.canvas_color.create_line(
                center_x, center_y, x1, y1, 
                fill=color, width=3, tags="color_wheel"
            )
        
        inner_radius = 30
        self.canvas_color.create_oval(
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius,
            fill='white', outline='#34495e', width=2
        )
    
    def hsv_to_rgb(self, h, s, v):
        """Convierte un color de HSV a RGB."""
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        
        if i == 0:
            return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1:
            return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2:
            return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3:
            return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4:
            return (int(t * 255), int(p * 255), int(v * 255))
        if i == 5:
            return (int(v * 255), int(p * 255), int(q * 255))
    
    def seleccionar_color_rueda(self, event):
        """Maneja el evento de clic en la rueda de colores."""
        center_x, center_y = 110, 110
        
        dx = event.x - center_x
        dy = event.y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if 30 < distance < 90:
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            hue = angle / 360
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color_hex = '#%02x%02x%02x' % rgb
            
            self.color_favorito.set(color_hex)
            self.color_display.configure(bg=color_hex)
            self.color_label.configure(text=color_hex)
            
            if GAME_AVAILABLE and self.game_preview:
                self.update_game_palette()
    
    def cambiar_tema(self, *args):
        """Cambia el esquema de colores según el tema seleccionado."""
        tema = self.tema_var.get()
        
        if tema == "oscuro":
            bg_frames = '#2d2d2d'
            fg_texto = '#ffffff'
        elif tema == "claro":
            bg_frames = '#ffffff'
            fg_texto = '#2c3e50'
        else:
            bg_frames = '#bdc3c7'
            fg_texto = '#2c3e50'
        
        self.color_frame.configure(bg=bg_frames, fg=fg_texto)
        self.tema_frame.configure(bg=bg_frames, fg=fg_texto)
        self.musica_frame.configure(bg=bg_frames, fg=fg_texto)
        self.canvas_color.configure(bg=bg_frames)
        self.color_info_frame.configure(bg=bg_frames)
        self.color_info_label.configure(bg=bg_frames, fg=fg_texto)
        self.color_label.configure(bg=bg_frames, fg=fg_texto)
        self.musica_label.configure(bg=bg_frames, fg=fg_texto)
        self.opciones_frame.configure(bg=bg_frames)
        self.rb_oscuro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_claro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_medio.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.botones_frame.configure(bg=bg_frames)
        
        if GAME_AVAILABLE and self.game_preview:
            self.update_game_palette()
    
    def pausar_reanudar_musica(self):
        """Pausa o reanuda la música según el estado actual"""
        if not self.is_playing:
            return
        
        try:
            if AUDIO_PLAYER == 'vlc' and self.vlc_player:
                if self.is_paused:
                    self.vlc_player.play()
                    self.is_paused = False
                    self.btn_pausar.config(text="Pausar Música", bg='#3498db')
                    print("▶️ Música reanudada")
                else:
                    self.vlc_player.pause()
                    self.is_paused = True
                    self.btn_pausar.config(text="Reanudar Música", bg='#27ae60')
                    print("⏸️ Música pausada")
                    
            elif AUDIO_PLAYER == 'pygame':
                from pygame import mixer
                if self.is_paused:
                    mixer.music.unpause()
                    self.is_paused = False
                    self.btn_pausar.config(text="Pausar Música", bg='#3498db')
                    print("▶️ Música reanudada")
                else:
                    mixer.music.pause()
                    self.is_paused = True
                    self.btn_pausar.config(text="Reanudar Música", bg='#27ae60')
                    print("⏸️ Música pausada")
                    
        except Exception as e:
            print(f"Error al pausar/reanudar: {e}")
    
    def buscar_cancion(self):
        """Busca y reproduce la canción solicitada usando YouTube."""
        cancion = self.cancion_var.get().strip()
        
        if not cancion:
            messagebox.showwarning("Advertencia", "Por favor ingresa el nombre de una canción")
            return
        
        if not YT_DLP_AVAILABLE:
            messagebox.showerror(
                "Error",
                "La librería yt-dlp no está disponible.\n\nInstala: pip install yt-dlp"
            )
            return
        
        if not AUDIO_PLAYER:
            error_msg = "No hay reproductor de audio disponible.\n\n"
            if VLC_ERROR:
                error_msg += f"Error VLC: {VLC_ERROR}\n\n"
            if PYGAME_ERROR:
                error_msg += f"Error pygame: {PYGAME_ERROR}\n\n"
            error_msg += (
                "Soluciones:\n"
                "1. Instala VLC Media Player:\n"
                "   https://www.videolan.org/vlc/\n"
                "   Luego reinicia el programa\n\n"
                "2. O instala pygame:\n"
                "   pip install pygame"
            )
            messagebox.showerror("Error", error_msg)
            return
        
        # Mostrar qué reproductor se usará
        player_names = {'vlc': 'VLC', 'pygame': 'pygame'}
        print(f"🎵 Usando reproductor: {player_names.get(AUDIO_PLAYER, 'desconocido')}")
        
        self._stop_music()
        self.btn_buscar.config(state='disabled', text="Buscando...")
        self.root.update()
        
        self.music_thread = threading.Thread(
            target=self._download_and_play,
            args=(cancion,),
            daemon=True
        )
        self.music_thread.start()
    
    def _download_and_play(self, query):
        """Descarga y reproduce la canción en un hilo separado."""
        try:
            if AUDIO_PLAYER == 'vlc':
                # VLC: reproducir stream directamente sin descargar
                print("📥 Buscando stream de audio...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                    else:
                        entry = info
                    
                    title = entry.get('title', 'Desconocido')
                    uploader = entry.get('uploader', 'YouTube')
                    duration = entry.get('duration', 0)
                    stream_url = entry.get('url')
                
                print(f"✓ Canción encontrada: {title}")
                self._play_vlc_stream(stream_url)
                self.is_playing = True
                
            elif AUDIO_PLAYER == 'pygame':
                # pygame: descargar archivo
                print("📥 Descargando audio...")
                temp_dir = tempfile.gettempdir()
                output_path = os_module.path.join(temp_dir, 'youtube_audio')
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_path,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                    
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                    else:
                        entry = info
                    
                    title = entry.get('title', 'Desconocido')
                    uploader = entry.get('uploader', 'YouTube')
                    duration = entry.get('duration', 0)
                    downloaded_file = ydl.prepare_filename(entry)
                
                if not os_module.path.exists(downloaded_file):
                    import glob
                    possible_files = glob.glob(output_path + '*')
                    if possible_files:
                        downloaded_file = possible_files[0]
                    else:
                        raise RuntimeError("No se pudo encontrar el archivo descargado")
                
                print(f"✓ Archivo descargado: {downloaded_file}")
                self.current_song_file = downloaded_file
                
                from pygame import mixer
                mixer.music.load(downloaded_file)
                mixer.music.play()
                self.is_playing = True
                print("✓ Reproduciendo con pygame")
            
            self.root.after(0, lambda t=title, u=uploader, d=duration: self._on_music_ready(t, u, d))
            
        except Exception as ex:
            import traceback
            error_msg = str(ex)
            traceback_msg = traceback.format_exc()
            print(f"✗ Error: {error_msg}")
            print(traceback_msg)
            self.root.after(0, lambda msg=error_msg: self._on_music_error(msg))
    
    def _play_vlc_stream(self, stream_url):
        """Reproduce stream de audio con VLC"""
        import vlc
        import time
        
        print(f"🎵 Intentando reproducir con VLC...")
        
        if not self.vlc_instance:
            self.vlc_instance = vlc.Instance('--no-video', '--quiet')
        
        self.vlc_player = self.vlc_instance.media_player_new()
        media = self.vlc_instance.media_new(stream_url)
        self.vlc_player.set_media(media)
        
        # Configurar volumen
        self.vlc_player.audio_set_volume(100)
        
        print("▶️ Iniciando reproducción...")
        self.vlc_player.play()
        
        # Esperar y verificar estado
        start = time.time()
        while time.time() - start < 5:
            state = self.vlc_player.get_state()
            
            if state == vlc.State.Playing:
                print("✓ Reproduciendo correctamente")
                return
            elif state == vlc.State.Error:
                print("✗ Error en reproducción VLC")
                raise RuntimeError("VLC no pudo reproducir el stream")
            
            time.sleep(0.5)
        
        print(f"⚠ Estado final VLC: {self.vlc_player.get_state()}")
    
    def _on_music_ready(self, title, uploader, duration):
        """Se ejecuta cuando la música está lista"""
        self.btn_buscar.config(state='normal', text="Buscar Canción")
        self.btn_pausar.config(state='normal')  # Habilitar botón de pausa
        
        mensaje = (
            f"🎵 Reproduciendo de fondo:\n\n"
            f"Título: {title}\n"
            f"Canal: {uploader}\n"
            f"Duración: {self._format_duration(duration)}"
        )
        messagebox.showinfo("Reproduciendo", mensaje)
    
    def _on_music_error(self, error_msg):
        """Se ejecuta cuando hay un error"""
        self.btn_buscar.config(state='normal', text="Buscar Canción")
        messagebox.showerror("Error", f"No se pudo reproducir la canción:\n{error_msg}")
    
    def _stop_music(self):
        """Detiene la reproducción actual"""
        if self.is_playing:
            try:
                if AUDIO_PLAYER == 'vlc' and self.vlc_player:
                    self.vlc_player.stop()
                    self.vlc_player = None
                elif AUDIO_PLAYER == 'pygame':
                    from pygame import mixer
                    mixer.music.stop()
            except:
                pass
            self.is_playing = False
            self.is_paused = False
            self.btn_pausar.config(state='disabled', text="Pausar Música", bg='#3498db')
        
        if self.current_song_file and os_module.path.exists(self.current_song_file):
            try:
                os_module.remove(self.current_song_file)
            except:
                pass
            self.current_song_file = None
    
    def _format_duration(self, seconds):
        """Formatea la duración en segundos a formato MM:SS."""
        if not seconds:
            return "0:00"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def iniciar_juego(self):
        """Inicia el juego en una ventana independiente y cierra la ventana de personalización."""
        if not GAME_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "Los módulos del juego no están disponibles.\n\n"
                "Asegúrate de tener:\n- PaletaColores.py\n- VentanaPrincipal.py"
            )
            return
        
        try:
            color = self.color_favorito.get()
            tema = self.tema_var.get()
            cancion = self.cancion_var.get().strip()
            
            palette = generate_palette(color, tema)
            
            # Ocultar la ventana de personalización en lugar de destruirla
            self.root.withdraw()
            
            # Crear ventana independiente para el juego
            game_window = tk.Toplevel()
            game_window.title("Sistema de Aldeas - Juego")
            game_window.geometry("600x750")
            game_window.resizable(False, False)
            
            # Cuando se cierre la ventana del juego, cerrar toda la aplicación
            game_window.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_aplicacion(game_window))
            
            game_frame = VillageGame(game_window, width=600, height=750, initial_palette=palette)
            game_frame.pack()
            
        except Exception as e:
            self.root.deiconify()  # Mostrar ventana de personalización si hay error
            messagebox.showerror("Error", f"No se pudo iniciar el juego:\n{e}")
    
    def _cerrar_aplicacion(self, game_window):
        """Cierra la ventana del juego y toda la aplicación"""
        game_window.destroy()
        self.root.destroy()
    
    def _crear_panel_preview(self, parent):
        """Crea el panel derecho con el preview del juego."""
        if not GAME_AVAILABLE:
            self.game_preview = None
            return
        
        right_panel = tk.Frame(parent, bg='#2c3e50', relief='sunken', bd=3)
        right_panel.pack(side='right', fill='both', expand=True, padx=(0, 10), pady=10)
        
        preview_title = tk.Label(
            right_panel, 
            text="PREVIEW DEL JUEGO", 
            font=("Arial", 14, "bold"), 
            bg='#2c3e50', 
            fg='white'
        )
        preview_title.pack(pady=10)
        
        try:
            self.game_preview = VillageGame(right_panel, width=600, height=750)
            self.game_preview.pack(pady=5)
        except Exception as e:
            error_label = tk.Label(
                right_panel, 
                text=f"Error al crear preview:\n{e}",
                bg='#2c3e50', 
                fg='red', 
                font=("Arial", 10)
            )
            error_label.pack(pady=20)
            self.game_preview = None
    
    def update_game_palette(self):
        """Actualiza la paleta de colores del preview."""
        if not GAME_AVAILABLE or not self.game_preview:
            return
        
        try:
            color_base = self.color_favorito.get()
            tema = self.tema_var.get()
            
            palette = generate_palette(color_base, tema)
            self.game_preview.apply_new_palette(palette)
        except Exception as e:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorSelectorApp(root)
    root.mainloop()