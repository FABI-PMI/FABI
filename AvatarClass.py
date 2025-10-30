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
        self.velocidad = float(velocidad)   # px/s (hacia ARRIBA)
        self.color = color
        self.activo = True
    
    def mover(self, dt):
        if not self.activo:
            return
        self.posicion[1] -= self.velocidad * dt  # avanza hacia arriba
        if self.posicion[1] < 80:  # fuera de tablero (por encima del grid)
            self.activo = False
    
    def desactivar(self):
        self.activo = False

def _color_proyectil_por_avatar(nombre):
    mapa = {
        "Flechador": "#4169E1",
        "Escudero":  "#808080",
        "Leñador":   "#8B4513",
        "Caníbal":   "#DC143C",
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
        self.posicion = [0, 0]  # [col, row] en el grid
    
    def esta_vivo(self) -> bool:
        """Verifica si el avatar sigue vivo"""
        return self.vida > 0
    
    def recibir_daño(self, daño: int, gestor_puntos=None) -> int:
        """
        El avatar recibe daño
        Retorna los puntos ganados si gestor_puntos está presente
        """
        self.vida = max(0, self.vida - daño)
        
        puntos_ganados = 0
        if gestor_puntos:
            puntos_ganados = gestor_puntos.agregar_puntos(daño)
        
        return puntos_ganados
    
    def _puede_atacar(self, torre_en_frente: bool) -> bool:
        """Verifica si el avatar puede atacar"""
        if self._t_atacar > 0:
            return False
        if self.solo_torre_en_frente and not torre_en_frente:
            return False
        return True
    
    def _puede_mover(self) -> bool:
        """Verifica si el avatar puede moverse"""
        return self._t_mover <= 0
    
    def step(self, dt: float, torre_en_frente: bool = False) -> EstadoAccion:
        """
        Actualiza el estado del avatar y retorna las acciones a realizar
        dt: tiempo transcurrido en segundos
        """
        if not self.esta_vivo():
            return EstadoAccion(False, False)
        
        # Reducir cooldowns
        self._t_mover = max(0.0, self._t_mover - dt)
        self._t_atacar = max(0.0, self._t_atacar - dt)
        
        acciones = EstadoAccion()
        
        # Verificar si puede atacar
        if self._puede_atacar(torre_en_frente):
            acciones.atacar = True
            self._t_atacar = self.cd_atacar
        
        # Verificar si puede moverse
        if self._puede_mover():
            acciones.mover = True
            self._t_mover = self.cd_mover
        
        return acciones
    
    def mover_hacia_arriba(self):
        """Mueve el avatar una casilla hacia arriba (row - 1)"""
        self.posicion[1] = max(0, self.posicion[1] - 1)
    
    def get_color(self):
        """Retorna el color representativo del avatar"""
        colores = {
            "Flechador": "#4169E1",
            "Escudero": "#808080",
            "Leñador": "#8B4513",
            "Caníbal": "#DC143C"
        }
        return colores.get(self.nombre, "#000000")
    
    def get_icono(self):
        """Retorna el icono/emoji del avatar"""
        iconos = {
            "Flechador": "🏹",
            "Escudero": "🛡️",
            "Leñador": "🪓",
            "Caníbal": "👹"
        }
        return iconos.get(self.nombre, "👤")


class Flechador(Avatar):
    """Avatar de largo alcance - ataca torres desde lejos"""
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
    """Avatar tanque - mucha vida, daño moderado"""
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
    """Avatar de daño - ataca solo torres en frente"""
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
    """Avatar de daño extremo - lento pero devastador"""
    def __init__(self):
        super().__init__(
            vida=25,
            ataque=12,
            cd_mover=4.0,
            cd_atacar=3.0,
            solo_torre_en_frente=True,
            nombre="Caníbal"
        )


class GestorAvatares:
    """Gestiona el spawning, movimiento y actualización de avatares"""
    
    def __init__(self, grid_cols=5, nivel="FACIL", sistema_puntos=None):
        self.avatares = []
        self.grid_cols = grid_cols
        self.nivel = nivel
        self.sistema_puntos = sistema_puntos
        self.proyectiles = []
        self._grid_cfg = {"x": 150, "y": 100, "cell_size": 60}

        # Configuración de spawning
        self.tiempo_inicio = None
        self.ultimo_spawn = 0
        self.activo = False
        
        # Estadísticas
        self.avatares_spawneados = 0
        self.avatares_eliminados = 0
        self.avatares_llegaron_meta = 0
        
        # Tipos de avatares disponibles
        self.tipos_avatar = [Flechador, Escudero, Leñador, Canibal]
        
        # Configuración según nivel
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
            "DIFICIL": {
                "lambda": 0.20,
                "spawn_min": 3.0,
                "spawn_max": 10.0,
                "probabilidades": [0.3, 0.3, 0.25, 0.15]
            }
        }
    
    def iniciar(self):
        """Inicia el sistema de spawning"""
        self.tiempo_inicio = time.time()
        self.ultimo_spawn = self.tiempo_inicio
        self.activo = True
        print("   🎮 Sistema de spawning iniciado")
    
    def detener(self):
        """Detiene el sistema de spawning"""
        self.activo = False
        
    def _centro_avatar_px(self, avatar):
        cx = self._grid_cfg["x"] + avatar.posicion[0]*self._grid_cfg["cell_size"] + self._grid_cfg["cell_size"]//2
        cy = self._grid_cfg["y"] + avatar.posicion[1]*self._grid_cfg["cell_size"] + self._grid_cfg["cell_size"]//2
        return float(cx), float(cy)

    def _disparar_proyectil(self, avatar):
        """Dispara un proyectil desde el avatar"""
        x, y = self._centro_avatar_px(avatar)
        proy = ProyectilAvatar(
            x, y,
            damage=avatar.ataque,
            tipo=avatar.nombre,
            velocidad=180.0,
            color=_color_proyectil_por_avatar(avatar.nombre)
        )
        self.proyectiles.append(proy)
        print(f"   🔫 {avatar.nombre} dispara proyectil (daño: {avatar.ataque})")

    def _proyectil_colisiona_con_torre(self, proyectil, row, col):
        """Verifica si un proyectil colisiona con una torre"""
        cell = self._grid_cfg["cell_size"]
        cx = self._grid_cfg["x"] + col*cell + cell//2
        cy = self._grid_cfg["y"] + row*cell + cell//2
        dx = proyectil.posicion[0] - cx
        dy = proyectil.posicion[1] - cy
        return math.hypot(dx, dy) < 40

    def _actualizar_proyectiles(self, dt, torres_grid):
        """Actualiza posición de proyectiles y verifica colisiones con torres"""
        # Mover proyectiles
        for p in self.proyectiles:
            if p.activo:
                p.mover(dt)
        
        # Verificar colisiones
        for p in list(self.proyectiles):
            if not p.activo:
                continue
            for (row, col), torre in torres_grid.items():
                if not torre.activa:
                    continue
                if self._proyectil_colisiona_con_torre(p, row, col):
                    torre.recibir_damage(p.damage)
                    print(f"   💥 {p.tipo} impacta torre de {torre.tipo} (-{p.damage} HP) → {torre.vida_actual}/{torre.vida_maxima}")
                    p.desactivar()
                    break
        
        # Limpiar proyectiles inactivos
        self.proyectiles = [p for p in self.proyectiles if p.activo]

    def get_todos_proyectiles(self):
        """Retorna todos los proyectiles activos"""
        return list(self.proyectiles)

    def actualizar(self, dt, torres_grid, grid_config=None):
        """Actualiza el estado de todos los avatares y proyectiles"""
        if not self.activo:
            return
        
        if grid_config:
            self._grid_cfg = dict(grid_config)

        tiempo_actual = time.time()
        
        # Verificar si es momento de spawnear
        tiempo_desde_ultimo = tiempo_actual - self.ultimo_spawn
        tiempo_spawn_necesario = self.calcular_tiempo_spawn(tiempo_actual - self.tiempo_inicio)
        
        if tiempo_desde_ultimo >= tiempo_spawn_necesario:
            self.spawn_avatar()
            self.ultimo_spawn = tiempo_actual

        avatares_a_remover = []
        
        for avatar in self.avatares:
            if not avatar.esta_vivo():
                if avatar not in avatares_a_remover:
                    avatares_a_remover.append(avatar)
                continue

            if avatar.posicion[1] <= 0:
                if avatar not in avatares_a_remover:
                    avatares_a_remover.append(avatar)
                    self.avatares_llegaron_meta += 1
                continue

            torre_en_frente = self.hay_torre_en_frente(avatar, torres_grid)
            acciones = avatar.step(dt, torre_en_frente)

            # 🔫 Disparo para tipos de rango (Flechador, Escudero)
            if acciones.atacar and not avatar.solo_torre_en_frente:
                self._disparar_proyectil(avatar)
            
            # 🗡️ Golpe sólo si está en frente (Leñador, Caníbal)
            if acciones.atacar and avatar.solo_torre_en_frente and torre_en_frente:
                self.atacar_torre(avatar, torres_grid)

            if acciones.mover and not torre_en_frente:
                avatar.mover_hacia_arriba()

        for avatar in avatares_a_remover:
            if avatar in self.avatares:
                self.avatares.remove(avatar)

        # 🔄 Actualizar proyectiles y verificar colisiones con torres
        self._actualizar_proyectiles(dt, torres_grid)

    def calcular_tiempo_spawn(self, tiempo_transcurrido):
        """Calcula el tiempo entre spawns usando distribución exponencial"""
        config = self.config_nivel[self.nivel]
        
        # Tiempo base exponencial
        tiempo_exp = random.expovariate(config["lambda"])
        
        # Limitar entre min y max
        tiempo_spawn = max(config["spawn_min"], 
                          min(config["spawn_max"], tiempo_exp))
        
        return tiempo_spawn
    
    def seleccionar_tipo_avatar(self):
        """Selecciona un tipo de avatar según las probabilidades del nivel"""
        config = self.config_nivel[self.nivel]
        return random.choices(self.tipos_avatar, 
                            weights=config["probabilidades"])[0]
    
    def spawn_avatar(self):
        """Crea un nuevo avatar en una columna aleatoria"""
        tipo_avatar = self.seleccionar_tipo_avatar()
        avatar = tipo_avatar()
        
        # Posición inicial: columna aleatoria, fila inferior
        col = random.randint(0, self.grid_cols - 1)
        row = 8  # Fila inferior del grid (9 filas totales: 0-8)
        avatar.posicion = [col, row]
        
        self.avatares.append(avatar)
        self.avatares_spawneados += 1
        
        print(f"   🔵 {avatar.nombre} spawneado en columna {col} (Total: {len(self.avatares)} activos)")
    
    def hay_torre_en_frente(self, avatar, torres_grid):
        """Verifica si hay una torre activa en frente del avatar"""
        col, row = avatar.posicion
        
        if row > 0:
            celda_frente = (row - 1, col)
            return celda_frente in torres_grid and torres_grid[celda_frente].activa
        
        return False
    
    def atacar_torre(self, avatar, torres_grid):
        """El avatar ataca la torre en frente (melee)"""
        col, row = avatar.posicion
        
        if row > 0:
            celda_frente = (row - 1, col)
            if celda_frente in torres_grid:
                torre = torres_grid[celda_frente]
                if torre.activa:
                    torre.recibir_damage(avatar.ataque)
                    print(f"   💥 {avatar.nombre} ataca torre de {torre.tipo} "
                          f"(-{avatar.ataque} HP) → {torre.vida_actual}/{torre.vida_maxima}")
    
    def verificar_colisiones_proyectiles(self, proyectiles):
        """
        Verifica colisiones entre proyectiles de torres y avatares
        """
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
                    # Guardar si estaba vivo ANTES del daño
                    estaba_vivo = avatar.esta_vivo()
                    
                    # Aplicar daño
                    puntos_ganados = avatar.recibir_daño(proyectil.damage, gestor_puntos)
                    
                    # Marcar proyectil para remover
                    proyectil.desactivar()
                    if proyectil not in proyectiles_a_remover:
                        proyectiles_a_remover.append(proyectil)
                    
                    colisiones.append((proyectil, avatar))
                    
                    # Contar solo si acaba de morir
                    if estaba_vivo and not avatar.esta_vivo():
                        self.avatares_eliminados += 1
                        estado = "💀 Eliminado"
                    else:
                        estado = f"❤️ {avatar.vida}/{avatar.vida_maxima} HP"
                    
                    puntos_texto = f"(+{puntos_ganados} pts)" if gestor_puntos else ""
                    print(f"   🎯 Proyectil de {proyectil.tipo} impacta a {avatar.nombre} "
                          f"(-{proyectil.damage} HP) {puntos_texto} → {estado}")
                    
                    break
        
        # Remover proyectiles que colisionaron
        for proyectil in proyectiles_a_remover:
            if proyectil in proyectiles:
                proyectiles.remove(proyectil)
        
        return colisiones
    
    def proyectil_colisiona_con_avatar(self, proyectil, avatar):
        """
        Verifica si un proyectil colisiona con un avatar
        """
        cell_size = 60
        grid_x = 150
        grid_y = 100
        
        # Convertir posición del avatar [col, row] a píxeles
        avatar_col = avatar.posicion[0]
        avatar_row = avatar.posicion[1]
        
        # Centro de la celda donde está el avatar
        avatar_x = grid_x + (avatar_col * cell_size) + (cell_size // 2)
        avatar_y = grid_y + (avatar_row * cell_size) + (cell_size // 2)
        
        # Distancia entre proyectil y avatar
        dx = proyectil.posicion[0] - avatar_x
        dy = proyectil.posicion[1] - avatar_y
        distancia = math.sqrt(dx * dx + dy * dy)
        
        return distancia < 40
    
    def limpiar_avatares_muertos(self):
        """Elimina avatares muertos de la lista"""
        self.avatares = [a for a in self.avatares if a.esta_vivo()]
    
    def get_avatares_activos(self):
        """Retorna lista de avatares activos"""
        return [a for a in self.avatares if a.esta_vivo()]
    
    def remover_avatar(self, avatar):
        """Remueve un avatar específico de la lista"""
        if avatar in self.avatares:
            self.avatares.remove(avatar)
            print(f"   🗑️ Avatar {avatar.nombre} removido del juego")
    
    def get_estadisticas(self):
        """Retorna estadísticas del juego"""
        return {
            "spawneados": self.avatares_spawneados,
            "eliminados": self.avatares_eliminados,
            "llegaron_meta": self.avatares_llegaron_meta,
            "activos": len(self.get_avatares_activos())
        }