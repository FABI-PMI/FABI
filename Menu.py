import tkinter as tk

class Menu:
    def __init__(self, root):  
        self.root = root  
        self.root.title("Avatars VS Rooks - Menú") 
        self.root.configure(bg="#8A1C32") 
        self.root.geometry("1100x650")        
        self.root.resizable(False, False)
        
        main_container = tk.Frame(root, bg="#8A1C32")  
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        self.DescripcionMenu(main_container)
        self.BotonesNivel(main_container)
        self.BarrasFrecuencia(main_container)
        
    
    def DescripcionMenu(self, parent):
        desc_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=300)
        desc_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        desc_frame.pack_propagate(False)
        
        title_label = tk.Label(  
            desc_frame,
            text="📜 Instrucciones",
            font=('Georgia', 18, 'bold'),
            bg="#C9C9C9",
            fg="#2C3E50"
        )
        title_label.pack(pady=20)
        
        # Frame para el texto con scrollbar
        text_container = tk.Frame(desc_frame, bg="#C9C9C9")
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_container, bg="#7A7A7A", troughcolor="#C9C9C9")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_container,  
            wrap=tk.WORD,  
            font=('Georgia', 12),  
            bg="#FFFFFF",  
            fg="#333333",  
            relief=tk.FLAT, 
            borderwidth=0,  
            padx=15,  
            pady=15,
            yscrollcommand=scrollbar.set
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        self.text_area.tag_configure("center", justify='center')
        
        mensaje = """
        
BIENVENIDO 
A 
AVATARS VS ROOKS

══════════════════════

En esta parte podrás encontrar la herramientas necesarias para defenderte de LOS AVATARS,
las TORRES ELEMENTALES:

⛰️ Arena - $50
🪨 Roca - $100
💧 Agua - $150
🔥 Fuego - $150

PRESUPUESTO INICIAL: $600

Ajusta sus frecuencias de disparo 
según tu estrategia. Cada decisión 
puede marcar la diferencia.

Elige la dificultad y demuestra 
tu habilidad en el campo de batalla,
al seleccionarla el juego iniciará inmediatamente.

El destino de nuestra aldea 
está en tus manos.

¡MUCHOS ÉXITOS EN EL COMBATE! """

        self.text_area.insert('1.0', mensaje) 
        self.text_area.tag_add("center", "1.0", "end")
        self.text_area.config(state=tk.DISABLED)

    
    def BotonesNivel(self, parent): 
        buttons_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=300)  
        buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)  
        buttons_frame.pack_propagate(False)
        
        title = tk.Label(  
            buttons_frame, 
            text="⚔️ DIFICULTAD",
            font=('Georgia', 18, 'bold'),  
            bg="#C9C9C9", 
            fg="#2C3E50"
        )
        title.pack(pady=20)
        
        tk.Frame(buttons_frame, bg="#C9C9C9", height=50).pack() 
        
        buttons_config = [ 
            ("DIFÍCIL", self.NivelDificil, "#8B3A3A"),  
            ("MEDIO", self.NivelMedio, "#8B6F47"), 
            ("FÁCIL", self.NivelFacil, "#6B8B3D")  
        ]
        
        for text, command, color in buttons_config:
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                font=('Georgia', 15, 'bold'), 
                bg=color,  
                fg="white",  
                activebackground=self.darken_color(color), 
                activeforeground="white",  
                relief=tk.RAISED, 
                borderwidth=3,
                padx=20,  
                pady=20,  
                cursor='hand2',  
                width=14
            )
            btn.pack(pady=20) 
            
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=self.darken_color(c))) 
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c)) 
    

    def BarrasFrecuencia(self, parent):
        sliders_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=400)  
        sliders_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        sliders_frame.pack_propagate(False)
        
        title = tk.Label(  
            sliders_frame, 
            text="⚡ FRECUENCIA DISPARO ⚡",
            font=('Georgia', 18, 'bold'),  
            bg="#C9C9C9", 
            fg="#2C3E50"
        )
        title.pack(pady=15) 
        
        info_label = tk.Label(  
            sliders_frame, 
            text="(Segundos entre disparos: 1=rápido, 10=lento)",
            font=('Georgia', 10),  
            bg="#C9C9C9", 
            fg="#555555"
        )
        info_label.pack(pady=(0, 10))
        
        sliders_config = [ 
            ("⛰️  TORRE DE ARENA", "#C4A35A", "#A68A4D"), 
            ("🪨  TORRE DE ROCA", "#7A6F5D", "#5C5347"),  
            ("💧 TORRE DE AGUA", "#5B7C8D", "#4A6576"),  
            ("🔥 TORRE DE FUEGO", "#B85450", "#9A4541")
        ]
        
        self.Frecuencias = {} 
        
        for name, color, trough_color in sliders_config:
            self.create_slider(sliders_frame, name, color, trough_color)  
    
    def create_slider(self, parent, name, color, trough_color): 
        container = tk.Frame(parent, bg="#C9C9C9") 
        container.pack(fill=tk.X, padx=20, pady=6)
        
        label = tk.Label(  
            container,  
            text=name,  
            font=('Georgia', 12, 'bold'),  
            bg="#C9C9C9",  
            fg="#2C3E50"
        )
        label.pack(pady=(0, 5))
        
        slider_frame = tk.Frame(container, bg="#7A7A7A", relief=tk.SOLID, borderwidth=2)
        slider_frame.pack(fill=tk.X)
        
        inner_frame = tk.Frame(slider_frame, bg="#FFFFFF")
        inner_frame.pack(fill=tk.X, padx=12, pady=10)
        
        slider = tk.Scale(
            inner_frame,
            from_=1,  # Cambiado de 0 a 1 para evitar división por cero
            to=10,
            orient=tk.HORIZONTAL,
            showvalue=1,
            bg=color,
            fg="white",
            troughcolor=trough_color,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.RAISED,
            length=280,
            width=22,
            sliderlength=32,
            font=('Georgia', 10, 'bold')
        )
        slider.set(5)  # Valor predeterminado
        slider.pack(fill=tk.X)
        
        self.Frecuencias[name] = slider

    #Funciones Aux de las barras de frecuencia 
    def get_frecuencia(self, nombre):
        return self.Frecuencias[nombre].get()

    def get_all_frequencies(self):
        return {nombre: slider.get() for nombre, slider in self.Frecuencias.items()}
    
    def mostrar_frecuencias(self):
        frecuencias = self.get_all_frequencies()
        print("\n" + "="*40)
        print(" FRECUENCIAS DE DISPARO CONFIGURADAS:")
        print("="*40)
        for nombre, valor in frecuencias.items():
            print(f"{nombre}: {valor} segundos entre disparos")
        print("="*40 + "\n")
    
    #Cambiar el boton de color cuando se va a seleccionar
    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.75)) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
    
    #Eleccion de Nivel
    def NivelDificil(self): 
        nivel = "DIFÍCIL"    
        print(f"Nivel {nivel} seleccionado")
        self.abrir_principal(nivel)                        


    def NivelMedio(self): 
        nivel = "MEDIO"     
        print(f"Nivel {nivel} seleccionado")
        self.abrir_principal(nivel)                        


    def NivelFacil(self):
        nivel = "FÁCIL"                             
        print(f"Nivel {nivel} seleccionado")
        self.abrir_principal(nivel)                        

    #Ventana
    def abrir_principal(self, nivel):
        # Obtener las frecuencias configuradas
        frecuencias = self.get_all_frequencies()
        
        print(f"Iniciando juego... Nivel: {nivel} | Presupuesto: $600")
        
        # Importar la ventana principal actualizada
        # Nota: Cambiar a VentanaPrincipal cuando se reemplace el archivo original
        try:
            from VentanaPrincipal import VillageGameWindow as VP
        except ImportError:
            print("Error: No se pudo importar VentanaPrincipalActualizada.py")
            print("Asegúrate de que el archivo esté en el mismo directorio.")
            return
        
        # Destruir la ventana del menú después de un pequeño delay
        self.root.after(50, self.root.destroy)
        
        # Crear la ventana del juego con el nivel y frecuencias
        ventana_juego = VP(nivel=nivel, frecuencias=frecuencias)
        ventana_juego.run()

def main():
    root = tk.Tk()
    app = Menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()