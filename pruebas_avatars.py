import tkinter as tk
import time
import random

# ----------------- Clases de Avatares -----------------
class EstadoAccion:
    def __init__(self, atacar=False, mover=False):
        self.atacar = atacar
        self.mover = mover

class Avatar:
    def __init__(self, vida, ataque, cd_mover, cd_atacar, solo_torre_en_frente=False, nombre=None):
        self.vida_maxima = vida
        self.vida = vida
        self.ataque = ataque
        self.cd_mover = cd_mover
        self.cd_atacar = cd_atacar
        self.solo_torre_en_frente = solo_torre_en_frente
        self.nombre = nombre or self.__class__.__name__
        self._t_mover = 0.0
        self._t_atacar = 0.0
        self.posicion = [0, 0]  # [col, row]

    def esta_vivo(self):
        return self.vida > 0

    def _puede_atacar(self, torre_en_frente):
        if self._t_atacar > 0:
            return False
        if self.solo_torre_en_frente and not torre_en_frente:
            return False
        return True

    def _puede_mover(self):
        return self._t_mover <= 0

    def step(self, dt, torre_en_frente=False):
        if not self.esta_vivo():
            return EstadoAccion(False, False)
        self._t_mover = max(0.0, self._t_mover - dt)
        self._t_atacar = max(0.0, self._t_atacar - dt)
        acciones = EstadoAccion()
        if self._puede_atacar(torre_en_frente):
            acciones.atacar = True
            self._t_atacar = self.cd_atacar
        if self._puede_mover():
            acciones.mover = True
            self._t_mover = self.cd_mover
        return acciones

    def mover_hacia_arriba(self):
        self.posicion[1] = max(0, self.posicion[1] - 1)

class Flechador(Avatar):
    def __init__(self):
        super().__init__(vida=5, ataque=2, cd_mover=10.0, cd_atacar=10.0, nombre="Flechador")

class Escudero(Avatar):
    def __init__(self):
        super().__init__(vida=10, ataque=3, cd_mover=10.0, cd_atacar=15.0, nombre="Escudero")

class Leñador(Avatar):
    def __init__(self):
        super().__init__(vida=20, ataque=9, cd_mover=13.0, cd_atacar=5.0, solo_torre_en_frente=True, nombre="Leñador")

class Canibal(Avatar):
    def __init__(self):
        super().__init__(vida=25, ataque=12, cd_mover=14.0, cd_atacar=3.0, solo_torre_en_frente=True, nombre="Caníbal")

# ----------------- Gestor de Avatares -----------------
class GestorAvatares:
    def __init__(self, grid_cols=5):
        self.avatares = []
        self.grid_cols = grid_cols
        self.tiempo_inicio = None
        self.ultimo_spawn = 0
        self.activo = False
        self.tipos_avatar = [Flechador, Escudero, Leñador, Canibal]
        self.config_nivel = {"FACIL": {"lambda": 0.15, "spawn_min": 3.0, "spawn_max": 12.0, "probabilidades": [0.5,0.3,0.15,0.05]}}
        self.nivel = "FACIL"

    def iniciar(self):
        self.tiempo_inicio = time.time()
        self.ultimo_spawn = self.tiempo_inicio
        self.activo = True
        print("🎮 Sistema de spawning iniciado")

    def calcular_tiempo_spawn(self):
        config = self.config_nivel[self.nivel]
        tiempo_exp = random.expovariate(config["lambda"])
        return max(config["spawn_min"], min(config["spawn_max"], tiempo_exp))

    def seleccionar_tipo_avatar(self):
        config = self.config_nivel[self.nivel]
        return random.choices(self.tipos_avatar, weights=config["probabilidades"])[0]

    def spawn_avatar(self):
        tipo_avatar = self.seleccionar_tipo_avatar()
        avatar = tipo_avatar()
        col = random.randint(0, self.grid_cols - 1)
        row = 8
        avatar.posicion = [col, row]
        self.avatares.append(avatar)
        print(f"🔵 {avatar.nombre} spawneado en columna {col} (Total: {len(self.avatares)} activos)")

    def update(self, dt, torres_grid):
        if not self.activo:
            return
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_spawn >= self.calcular_tiempo_spawn():
            self.spawn_avatar()
            self.ultimo_spawn = tiempo_actual
        for avatar in self.avatares[:]:
            if avatar.posicion[1] <= 0:
                self.avatares.remove(avatar)
                continue
            avatar.step(dt)
            avatar.mover_hacia_arriba()

# ----------------- Ventana principal -----------------
root = tk.Tk()
root.title("Prueba de Avatares")
canvas = tk.Canvas(root, width=400, height=600, bg="white")
canvas.pack()

gestor = GestorAvatares()
gestor.iniciar()
torres_grid = {}  # vacio, por ahora no hay torres

def dibujar_avatares():
    canvas.delete("avatar")
    for avatar in gestor.avatares:
        x = 50 + avatar.posicion[0]*60
        y = 500 - avatar.posicion[1]*60
        canvas.create_oval(x-20, y-20, x+20, y+20, fill="red", tags="avatar")
        canvas.create_text(x, y, text=avatar.nombre[0], fill="white", tags="avatar")

def loop_juego():
    dt = 0.1
    gestor.update(dt, torres_grid)
    dibujar_avatares()
    root.after(100, loop_juego)

loop_juego()
root.mainloop()
