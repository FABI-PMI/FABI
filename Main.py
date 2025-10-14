"""
Archivo principal del juego - Avatar vs Rooks
Muestra splash screen y luego el sistema de login
"""
import tkinter as tk
from SplashScreen import SplashScreen
from Registro import Registro


def main():
    # Crear ventana raíz (permanece oculta)
    root = tk.Tk()
    root.withdraw()
    
    # Mostrar splash screen
    splash = SplashScreen(root, logo_path="Logo.jpg", duration=3000)
    
    def mostrar_login():
        """Se ejecuta después de que el splash se cierra"""
        # Crear ventana de login
        login_window = tk.Toplevel(root)
        
        # Iniciar el login (sin callback, solo pasando la ventana)
        Registro(login_window)
        
        # Si el usuario cierra la ventana de login
        login_window.protocol("WM_DELETE_WINDOW", lambda: [login_window.destroy(), root.quit()])
    
    # Programar que el login aparezca después del splash (3 segundos)
    root.after(3000, mostrar_login)
    
    # Iniciar el loop principal
    root.mainloop()


if __name__ == "__main__":
    main() 