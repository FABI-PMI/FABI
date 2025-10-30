import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen:
    def __init__(self, root, logo_path="Logo.jpg", duration=3000):
        """
        Pantalla de carga inicial
        
        Args:
            root: Ventana padre de Tkinter
            logo_path: Ruta al logo
            duration: Duración en milisegundos (por defecto 3000 = 3 segundos)
        """
        self.root = root
        self.duration = duration
        self.logo_path = logo_path
        
        # Crear ventana splash
        self.splash = tk.Toplevel(root)
        self.splash.title("")
        
        # Configurar tamaño y posición
        splash_width = 600
        splash_height = 400
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        
        self.splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
        
        # Sin bordes
        self.splash.overrideredirect(True)
        
        # Fondo sólido rojo oscuro
        self.canvas = tk.Canvas(
            self.splash,
            width=splash_width,
            height=splash_height,
            bg='#8A1C32',  # Color sólido
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Agregar logo
        self.agregar_logo()
        
        # Agregar título
        self.canvas.create_text(
            splash_width // 2,
            100,
            text="Avatar vs Rooks",
            font=("Arial", 42, "bold"),
            fill="white"
        )
        
        # Agregar puntos de carga animados
        self.dots_y = 280
        self.dots = []
        self.dot_index = 0
        self.crear_puntos_carga(splash_width)
        
        # Texto "Por favor espere..."
        self.canvas.create_text(
            splash_width // 2,
            320,
            text="Por favor espere...",
            font=("Arial", 14),
            fill="white"
        )
        
        # Iniciar animación
        self.animar_puntos()
        
        # Cerrar después del tiempo especificado
        self.splash.after(self.duration, self.cerrar)
    
    def agregar_logo(self):
        """Agrega el logo en el centro"""
        try:
            if os.path.exists(self.logo_path):
                # Cargar y redimensionar logo
                img = Image.open(self.logo_path)
                img = img.resize((200, 200), Image.LANCZOS)
                
                self.logo_img = ImageTk.PhotoImage(img)
                
                # Colocar logo
                self.canvas.create_image(
                    300, 200,
                    image=self.logo_img
                )
            else:
                # Si no existe el logo, mostrar texto alternativo
                self.canvas.create_text(
                    300, 200,
                    text="🎮",
                    font=("Arial", 80),
                    fill="white"
                )
        except Exception as e:
            print(f"Error al cargar logo: {e}")
            # Mostrar emoji como alternativa
            self.canvas.create_text(
                300, 200,
                text="🎮",
                font=("Arial", 80),
                fill="white"
            )
    
    def crear_puntos_carga(self, width):
        """Crea los puntos de animación de carga"""
        center_x = width // 2
        spacing = 25
        
        for i in range(3):
            x = center_x - spacing + (i * spacing)
            dot = self.canvas.create_oval(
                x - 5, self.dots_y - 5,
                x + 5, self.dots_y + 5,
                fill="white",
                outline=""
            )
            self.dots.append(dot)
    
    def animar_puntos(self):
        """Anima los puntos de carga"""
        if not self.splash.winfo_exists():
            return
            
        # Resetear todos los puntos a tamaño normal
        for i, dot in enumerate(self.dots):
            center_x = 300 - 25 + (i * 25)
            self.canvas.coords(
                dot,
                center_x - 5, self.dots_y - 5,
                center_x + 5, self.dots_y + 5
            )
            self.canvas.itemconfig(dot, fill="white")
        
        # Hacer más grande el punto actual
        current_dot = self.dots[self.dot_index]
        center_x = 300 - 25 + (self.dot_index * 25)
        self.canvas.coords(
            current_dot,
            center_x - 8, self.dots_y - 8,
            center_x + 8, self.dots_y + 8
        )
        self.canvas.itemconfig(current_dot, fill="#FFFFFF")  # Dorado
        
        # Siguiente punto
        self.dot_index = (self.dot_index + 1) % 3
        
        # Continuar animación
        self.splash.after(400, self.animar_puntos)
    
    def cerrar(self):
        """Cierra la ventana splash"""
        try:
            self.splash.destroy()
        except:
            pass


def mostrar_splash(root, callback, logo_path="Logo.jpg", duration=3000):
    """
    Función auxiliar para mostrar el splash screen
    
    Args:
        root: Ventana principal
        callback: Función a ejecutar después de cerrar el splash
        logo_path: Ruta al logo
        duration: Duración en milisegundos
    """
    splash = SplashScreen(root, logo_path, duration)
    root.after(duration, callback)


if __name__ == "__main__":
    # Ejemplo de uso
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    def mostrar_ventana_principal():
        root.deiconify()
        root.geometry("400x300")
        tk.Label(root, text="Ventana Principal", font=("Arial", 20)).pack(pady=100)
    
    mostrar_splash(root, mostrar_ventana_principal)
    root.mainloop()