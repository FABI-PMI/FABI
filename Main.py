"""
Archivo principal del juego - Avatar vs Rooks
Muestra splash screen y luego el sistema de login   
"""
import tkinter as tk
from SplashScreen import SplashScreen


def main():
    # Crear ventana raíz temporal solo para el splash
    splash_root = tk.Tk()
    splash_root.withdraw()
    
    # Mostrar splash screen
    splash = SplashScreen(splash_root, logo_path="Logo.jpg", duration=3000)
    
    def mostrar_login():
        """Se ejecuta después de que el splash se cierra"""
        # Destruir la ventana del splash
        splash_root.destroy()
        
        # Crear nueva ventana raíz para el login
        login_root = tk.Tk()
        
        # Importar LoginApp aquí para evitar problemas de importación circular
        from Login import LoginApp
        
        # Iniciar el login con la nueva ventana raíz
        app = LoginApp(login_root)
        
        # Iniciar el loop de la ventana de login
        login_root.mainloop()
    
    # Programar que el login aparezca después del splash (3 segundos)
    splash_root.after(3000, mostrar_login)
    
    # Iniciar el loop del splash
    splash_root.mainloop()


if __name__ == "__main__":
    main()
