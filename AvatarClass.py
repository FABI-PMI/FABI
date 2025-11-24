import time
import random
import math

class EstadoAccion:
    """Representa las acciones que puede realizar un avatar en un frame"""
    def __init__(self, atacar=False, mover=False):
        self.atacar = atacar
        self.mover = mover

class ProyectilAvatar:
    def __init__(self, x, y, damage, tipo="Avatar", velocidad=180.0, color="#2222FF"):
        self.posicion = [float(x), float(y)]
        self.damage = int(damage)
        self.tipo = tipo
        self.velocidad = float(velocidad)
        self.color = color
        self.activo = True
    
    def mover(self, dt):
        if not self.activo:
            return
        self.posicion[1] -= self.velocidad * dt
        if self.posicion[1] < 80:
            self.activo = False
    
    def desactivar(self):
        self.activo = False

def _color_proyectil_por_avatar(nombre):
    mapa = {
        "Flechador": "#4169E1",
        "Escudero":  "#808080",
        "Leñador":   "#8B4513",
        "Canibal":   "#DC143C",
    }
    return mapa.get(nombre, "#000000")

class Avatar:
    """Clase base para todos los avatares/enemigos"""
    nombre: str = "Avatar"
    
    def __init__(self, vida: int, ataque: int, cd_mover: float, cd_atacar: float,
                 solo_torre_en_frente: bool = False, nombre: str = None):
        self.vida_maxima = vida
        self.vida = vida
        self.ataque = ataque
        self.cd_mover = cd_mover
        self.cd_atacar = cd_atacar
        self.solo_torre_en_frente = solo_torre_en_frente
        self.nombre = nombre or self.__class__.__name__
        self._t_mover = 0.0
        self._t_atacar = 0.0
        self.posicion = [0, 0]
        # Sistema de animacion de ataque melee
        self.esta_atacando_melee = False
        self.tiempo_inicio_ataque = 0.0
        self.duracion_animacion_ataque = 0.5  # duracion de la animacion de ataque en segundos
    
    def esta_vivo(self) -> bool:
        return self.vida > 0
    
    def recibir_dano(self, dano: int, gestor_puntos=None) -> int:
        self.vida = max(0, self.vida - dano)
        
        puntos_ganados = 0
        if gestor_puntos:
            puntos_ganados = gestor_puntos.agregar_puntos(dano)
        
        return puntos_ganados
    
    def _puede_atacar(self, torre_en_frente: bool) -> bool:
        if self._t_atacar > 0:
            return False
        if self.solo_torre_en_frente and not torre_en_frente:
            return False
        return True
    
    def _puede_mover(self) -> bool:
        return self._t_mover <= 0
    
    def step(self, dt: float, torre_en_frente: bool = False) -> EstadoAccion:
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
    
    def iniciar_ataque_melee(self):
        """Inicia la animacion de ataque melee"""
        import time
        self.esta_atacando_melee = True
        self.tiempo_inicio_ataque = time.time()
    
    def actualizar_estado_ataque(self):
        """Actualiza el estado de la animacion de ataque"""
        import time
        if self.esta_atacando_melee:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_ataque
            if tiempo_transcurrido >= self.duracion_animacion_ataque:
                self.esta_atacando_melee = False
    
    def get_frame_arma(self):
        """Obtiene el frame actual de la animacion del arma (0 o 1)"""
        if not self.esta_atacando_melee:
            return None
        import time
        tiempo_transcurrido = time.time() - self.tiempo_inicio_ataque
        # Alterna entre 0 y 1 cada 0.1 segundos
        return int((tiempo_transcurrido * 10) % 2)
    
    def get_color(self):
        colores = {
            "Flechador": "#4169E1",
            "Escudero": "#808080",
            "Leñador": "#8B4513",
            "Canibal": "#DC143C"
        }
        return colores.get(self.nombre, "#000000")
    
    def get_icono(self):
        iconos = {
            "Flechador": "🏹",
            "Escudero": "🛡️",
            "Leñador": "🪓",
            "Canibal": "💹"
        }
        return iconos.get(self.nombre, "👤")


class Flechador(Avatar):
    def __init__(self):
        super().__init__(
            vida=5,
            ataque=2,
            cd_mover=2.0,
            cd_atacar=5.0,
            solo_torre_en_frente=False,
            nombre="Flechador"
        )


class Escudero(Avatar):
    def __init__(self):
        super().__init__(
            vida=10,
            ataque=3,
            cd_mover=2.5,
            cd_atacar=8.0,
            solo_torre_en_frente=False,
            nombre="Escudero"
        )


class Leñador(Avatar):
    def __init__(self):
        super().__init__(
            vida=20,
            ataque=9,
            cd_mover=3.0,
            cd_atacar=5.0,
            solo_torre_en_frente=True,
            nombre="Leñador"
        )


class Canibal(Avatar):
    def __init__(self):
        super().__init__(
            vida=25,
            ataque=12,
            cd_mover=4.0,
            cd_atacar=3.0,
            solo_torre_en_frente=True,
            nombre="Canibal"
        )


class GestorAvatares:
    def __init__(self, grid_cols=5, nivel="FACIL", sistema_puntos=None):
        self.avatares = []
        self.grid_cols = grid_cols
        self.nivel = nivel
        self.sistema_puntos = sistema_puntos
        self.proyectiles = []
        self._grid_cfg = {"x": 150, "y": 100, "cell_size": 60}
        self.grid_ref = None  # Referencia al objeto Grid para colisiones

        self.tiempo_inicio = None
        self.ultimo_spawn = 0
        self.activo = False
        
        self.avatares_spawneados = 0
        self.avatares_eliminados = 0
        self.avatares_llegaron_meta = 0
        
        self.tipos_avatar = [Flechador, Escudero, Leñador, Canibal]
        
        self.config_nivel = {
            "FACIL": {
                "lambda": 0.10,
                "spawn_min": 5.0,
                "spawn_max": 15.0,
                "probabilidades": [0.5, 0.3, 0.15, 0.05]
            },
            "MEDIO": {
                "lambda": 0.15,
                "spawn_min": 4.0,
                "spawn_max": 12.0,
                "probabilidades": [0.4, 0.3, 0.2, 0.1]
            },
            "DIFÍCIL": {
                "lambda": 0.20,
                "spawn_min": 3.0,
                "spawn_max": 10.0,
                "probabilidades": [0.3, 0.3, 0.25, 0.15]
            }
        }
    
    def iniciar(self):
        self.tiempo_inicio = time.time()
        self.ultimo_spawn = self.tiempo_inicio
        self.activo = True
        print("   🎮 Sistema de spawning iniciado")
    
    def detener(self):
        self.activo = False
        
    def _centro_avatar_px(self, avatar):
        cx = self._grid_cfg["x"] + avatar.posicion[0]*self._grid_cfg["cell_size"] + self._grid_cfg["cell_size"]//2
        cy = self._grid_cfg["y"] + avatar.posicion[1]*self._grid_cfg["cell_size"] + self._grid_cfg["cell_size"]//2
        return float(cx), float(cy)

    def _disparar_proyectil(self, avatar):
        x, y = self._centro_avatar_px(avatar)
        proy = ProyectilAvatar(
            x, y,
            damage=avatar.ataque,
            tipo=avatar.nombre,
            velocidad=180.0,
            color=_color_proyectil_por_avatar(avatar.nombre)
        )
        self.proyectiles.append(proy)
        print(f"   🔫 {avatar.nombre} dispara proyectil (dano: {avatar.ataque})")

    def _proyectil_colisiona_con_torre(self, proyectil, row, col):
        cell = self._grid_cfg["cell_size"]
        cx = self._grid_cfg["x"] + col*cell + cell//2
        cy = self._grid_cfg["y"] + row*cell + cell//2
        dx = proyectil.posicion[0] - cx
        dy = proyectil.posicion[1] - cy
        return math.hypot(dx, dy) < 40

    def _actualizar_proyectiles(self, dt, torres_grid):
        for p in self.proyectiles:
            if p.activo:
                p.mover(dt)
        
        for p in list(self.proyectiles):
            if not p.activo:
                continue
            for (row, col), torre in torres_grid.items():
                if not torre.activa:
                    continue
                if self._proyectil_colisiona_con_torre(p, row, col):
                    torre.recibir_damage(p.damage)
                    print(f"   💥 {p.tipo} impacta torre de {torre.tipo} (-{p.damage} HP) -> {torre.vida_actual}/{torre.vida_maxima}")
                    
                    # Agregar animacion de colision
                    if self.grid_ref:
                        cell = self._grid_cfg["cell_size"]
                        cx = self._grid_cfg["x"] + col*cell + cell//2
                        cy = self._grid_cfg["y"] + row*cell + cell//2
                        self.grid_ref.agregar_colision(cx, cy)
                    
                    p.desactivar()
                    break
        
        self.proyectiles = [p for p in self.proyectiles if p.activo]

    def get_todos_proyectiles(self):
        return list(self.proyectiles)

    def actualizar(self, dt, torres_grid, grid_config=None):
        if not self.activo:
            return
        
        if grid_config:
            self._grid_cfg = dict(grid_config)

        tiempo_actual = time.time()
        
        tiempo_desde_ultimo = tiempo_actual - self.ultimo_spawn
        tiempo_spawn_necesario = self.calcular_tiempo_spawn(tiempo_actual - self.tiempo_inicio)
        
        if tiempo_desde_ultimo >= tiempo_spawn_necesario:
            self.spawn_avatar()
            self.ultimo_spawn = tiempo_actual

        avatares_a_remover = []
        
        for avatar in self.avatares:
            # Verificar primero si el avatar está muerto
            if not avatar.esta_vivo():
                if avatar not in avatares_a_remover:
                    avatares_a_remover.append(avatar)
                continue
            
            # Actualizar estado de animacion de ataque solo si está vivo
            avatar.actualizar_estado_ataque()

            if avatar.posicion[1] <= 0:
                if avatar not in avatares_a_remover:
                    avatares_a_remover.append(avatar)
                    self.avatares_llegaron_meta += 1
                continue

            torre_en_frente = self.hay_torre_en_frente(avatar, torres_grid)
            acciones = avatar.step(dt, torre_en_frente)

            # Solo disparar si el avatar está vivo
            if acciones.atacar and not avatar.solo_torre_en_frente and avatar.esta_vivo():
                self._disparar_proyectil(avatar)
            
            # NO generamos colision aqui para ataques melee (lenador/canibal)
            # porque queremos animacion de arma, no de colision
            if acciones.atacar and avatar.solo_torre_en_frente and torre_en_frente and avatar.esta_vivo():
                self.atacar_torre(avatar, torres_grid)

            if acciones.mover and not torre_en_frente:
                avatar.mover_hacia_arriba()

        for avatar in avatares_a_remover:
            if avatar in self.avatares:
                self.avatares.remove(avatar)

        self._actualizar_proyectiles(dt, torres_grid)

    def calcular_tiempo_spawn(self, tiempo_transcurrido):
        config = self.config_nivel[self.nivel]
        tiempo_exp = random.expovariate(config["lambda"])
        tiempo_spawn = max(config["spawn_min"], 
                          min(config["spawn_max"], tiempo_exp))
        return tiempo_spawn
    
    def seleccionar_tipo_avatar(self):
        config = self.config_nivel[self.nivel]
        return random.choices(self.tipos_avatar, 
                            weights=config["probabilidades"])[0]
    
    def spawn_avatar(self):
        tipo_avatar = self.seleccionar_tipo_avatar()
        avatar = tipo_avatar()
        
        col = random.randint(0, self.grid_cols - 1)
        row = 8
        avatar.posicion = [col, row]
        
        self.avatares.append(avatar)
        self.avatares_spawneados += 1
        
        print(f"   🔵 {avatar.nombre} spawneado en columna {col} (Total: {len(self.avatares)} activos)")
    
    def hay_torre_en_frente(self, avatar, torres_grid):
        col, row = avatar.posicion
        
        if row > 0:
            celda_frente = (row - 1, col)
            return celda_frente in torres_grid and torres_grid[celda_frente].activa
        
        return False
    
    def atacar_torre(self, avatar, torres_grid):
        col, row = avatar.posicion
        
        # Iniciar animacion de ataque melee
        avatar.iniciar_ataque_melee()
        
        if row > 0:
            celda_frente = (row - 1, col)
            if celda_frente in torres_grid:
                torre = torres_grid[celda_frente]
                if torre.activa:
                    torre.recibir_damage(avatar.ataque)
                    print(f"   💥 {avatar.nombre} ataca torre de {torre.tipo} "
                          f"(-{avatar.ataque} HP) -> {torre.vida_actual}/{torre.vida_maxima}")
    
    def verificar_colisiones_proyectiles(self, proyectiles):
        colisiones = []
        proyectiles_a_remover = []
        
        gestor_puntos = self.sistema_puntos
        
        for proyectil in proyectiles:
            if not proyectil.activo:
                continue
            
            for avatar in self.avatares:
                if not avatar.esta_vivo():
                    continue
                
                if self.proyectil_colisiona_con_avatar(proyectil, avatar):
                    estaba_vivo = avatar.esta_vivo()
                    
                    puntos_ganados = avatar.recibir_dano(proyectil.damage, gestor_puntos)
                    
                    # Agregar animacion de colision
                    if self.grid_ref:
                        x, y = self._centro_avatar_px(avatar)
                        self.grid_ref.agregar_colision(x, y)
                    
                    proyectil.desactivar(por_impacto=True)
                    if proyectil not in proyectiles_a_remover:
                        proyectiles_a_remover.append(proyectil)
                    
                    colisiones.append((proyectil, avatar))
                    
                    if estaba_vivo and not avatar.esta_vivo():
                        self.avatares_eliminados += 1
                        estado = "💀 Eliminado"
                    else:
                        estado = f"❤️ {avatar.vida}/{avatar.vida_maxima} HP"
                    
                    puntos_texto = f"(+{puntos_ganados} pts)" if gestor_puntos else ""
                    print(f"   🎯 Proyectil de {proyectil.tipo} impacta a {avatar.nombre} "
                          f"(-{proyectil.damage} HP) {puntos_texto} -> {estado}")
                    
                    break
        
        for proyectil in proyectiles_a_remover:
            if proyectil in proyectiles:
                proyectiles.remove(proyectil)
        
        return colisiones
    
    def proyectil_colisiona_con_avatar(self, proyectil, avatar):
        cell_size = 60
        grid_x = 150
        grid_y = 100
        
        avatar_col = avatar.posicion[0]
        avatar_row = avatar.posicion[1]
        
        avatar_x = grid_x + (avatar_col * cell_size) + (cell_size // 2)
        avatar_y = grid_y + (avatar_row * cell_size) + (cell_size // 2)
        
        dx = proyectil.posicion[0] - avatar_x
        dy = proyectil.posicion[1] - avatar_y
        distancia = math.sqrt(dx * dx + dy * dy)
        
        return distancia < 40
    
    def limpiar_avatares_muertos(self):
        self.avatares = [a for a in self.avatares if a.esta_vivo()]
    
    def get_avatares_activos(self):
        return [a for a in self.avatares if a.esta_vivo()]
    
    def remover_avatar(self, avatar):
        if avatar in self.avatares:
            self.avatares.remove(avatar)
            print(f"   🗑️ Avatar {avatar.nombre} removido del juego")
    
    def get_estadisticas(self):
        return {
            "spawneados": self.avatares_spawneados,
            "eliminados": self.avatares_eliminados,
            "llegaron_meta": self.avatares_llegaron_meta,
            "activos": len(self.get_avatares_activos())
        }