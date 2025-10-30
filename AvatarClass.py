"""
Sistema de Avatares (Enemigos) para Avatars vs Rooks
Incluye: spawning exponencial, movimiento, ataque y colisiones
"""
import random
import time
import math


class EstadoAccion:
    def __init__(self, atacar=False, mover=False):
        self.atacar = atacar
        self.mover = mover


class Avatar:
    """Clase base para todos los avatares enemigos"""
    nombre: str = "Avatar"
    
    def __init__(self, vida: int, ataque: int, cd_mover: float, cd_atacar: float,
                 solo_torre_en_frente: bool = False, nombre: str = None, posicion=None):
        self.vida_maxima = vida
        self.vida = vida
        self.ataque = ataque
        self.cd_mover = cd_mover
        self.cd_atacar = cd_atacar
        self.solo_torre_en_frente = solo_torre_en_frente
        self.nombre = nombre or self.__class__.__name__
        self._t_mover = 0.0
        self._t_atacar = 0.0
        
        # Posición en el grid [col, row]
        self.posicion = posicion or [0, 0]
        self.posicion_pixel = [0, 0]  # Posición en píxeles para animación
        
        # Estado
        self.activo = True
        self.llegó_a_meta = False
        
    def esta_vivo(self) -> bool:
        return self.vida > 0 and self.activo
    
    def recibir_daño(self, daño: int, gestor_puntos=None) -> int:
        """
        Recibe daño y retorna los puntos ganados
        Cada punto de vida perdido = 1 punto
        """
        daño_real = min(daño, self.vida)  # No puede hacer más daño que la vida restante
        self.vida = max(0, self.vida - daño)
        
        if not self.esta_vivo():
            self.activo = False
        
        # Agregar puntos al gestor si existe
        if gestor_puntos:
            gestor_puntos.agregar_puntos(daño_real)
        
        return daño_real  # Retorna los puntos ganados
    
    def _puede_atacar(self, torre_en_frente: bool) -> bool:
        if self._t_atacar > 0:
            return False
        if self.solo_torre_en_frente and not torre_en_frente:
            return False
        return True
    
    def _puede_mover(self) -> bool:
        return self._t_mover <= 0
    
    def step(self, dt: float, torre_en_frente: bool = False) -> EstadoAccion:
        """Actualiza el estado del avatar y retorna las acciones que puede realizar"""
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
        """Mueve el avatar una celda hacia arriba (hacia las casas)"""
        if self.posicion[1] > 0:
            self.posicion[1] -= 1
        else:
            self.llegó_a_meta = True
            self.activo = False
    
    def get_color(self):
        """Retorna el color del avatar según su tipo"""
        return "#FF4444"  # Rojo por defecto
    
    def get_icono(self):
        """Retorna el icono del avatar"""
        return "👤"


class Flechador(Avatar):
    def __init__(self, posicion=None):
        super().__init__(vida=5, ataque=2, cd_mover=10.0, cd_atacar=10.0,
                         solo_torre_en_frente=False, nombre="Flechador", posicion=posicion)
        self.color = "#8B4513"  # Marrón
        self.icono = "🏹"
    
    def get_color(self):
        return self.color
    
    def get_icono(self):
        return self.icono


class Escudero(Avatar):
    def __init__(self, posicion=None):
        super().__init__(vida=10, ataque=3, cd_mover=10.0, cd_atacar=15.0,
                         solo_torre_en_frente=False, nombre="Escudero", posicion=posicion)
        self.color = "#4169E1"  # Azul real
        self.icono = "🛡️"
    
    def get_color(self):
        return self.color
    
    def get_icono(self):
        return self.icono


class Leñador(Avatar):
    def __init__(self, posicion=None):
        super().__init__(vida=20, ataque=9, cd_mover=13.0, cd_atacar=5.0,
                         solo_torre_en_frente=True, nombre="Leñador", posicion=posicion)
        self.color = "#228B22"  # Verde bosque
        self.icono = "🪓"
    
    def get_color(self):
        return self.color
    
    def get_icono(self):
        return self.icono


class Canibal(Avatar):
    def __init__(self, posicion=None):
        super().__init__(vida=25, ataque=12, cd_mover=14.0, cd_atacar=3.0,
                         solo_torre_en_frente=True, nombre="Caníbal", posicion=posicion)
        self.color = "#8B008B"  # Púrpura oscuro
        self.icono = "👹"
    
    def get_color(self):
        return self.color
    
    def get_icono(self):
        return self.icono


class GestorAvatares:
    """Gestiona el spawning exponencial y actualización de avatares"""
    
    def __init__(self, grid_cols=5, nivel="FACIL"):
        self.avatares = []
        self.grid_cols = grid_cols
        self.nivel = nivel
        self.tiempo_inicio = None
        self.ultimo_spawn = 0
        self.activo = False
        self.tipos_avatar = [Flechador, Escudero, Leñador, Canibal]
        
        self.config_nivel = {
            "FACIL": {"lambda": 0.15, "spawn_min": 3.0, "spawn_max": 12.0, "probabilidades": [0.5, 0.3, 0.15, 0.05]},
            "MEDIO": {"lambda": 0.25, "spawn_min": 2.0, "spawn_max": 10.0, "probabilidades": [0.4, 0.35, 0.2, 0.05]},
            "DIFICIL": {"lambda": 0.35, "spawn_min": 1.5, "spawn_max": 8.0, "probabilidades": [0.3, 0.35, 0.25, 0.1]},
            "PRUEBA": {"lambda": 0.2, "spawn_min": 2.5, "spawn_max": 10.0, "probabilidades": [0.4, 0.3, 0.2, 0.1]}
        }
        
        self.config = self.config_nivel.get(nivel.upper(), self.config_nivel["FACIL"])
        self.proximo_spawn = self.calcular_tiempo_spawn()
        self.avatares_spawneados = 0
        self.avatares_eliminados = 0
        self.avatares_llegaron_meta = 0
        self.sistema_puntos = None
    
    def calcular_tiempo_spawn(self):
        lambda_param = self.config["lambda"]
        tiempo_exp = random.expovariate(lambda_param)
        return max(self.config["spawn_min"], min(tiempo_exp, self.config["spawn_max"]))
    
    def seleccionar_tipo_avatar(self):
        return random.choices(self.tipos_avatar, weights=self.config["probabilidades"], k=1)[0]
    
    def iniciar(self):
        self.tiempo_inicio = time.time()
        self.ultimo_spawn = 0
        self.activo = True
        print(f"\n🎮 Sistema de spawning iniciado - Nivel: {self.nivel}")
        print(f"   Parámetros: λ={self.config['lambda']}, min={self.config['spawn_min']}s, max={self.config['spawn_max']}s")
    
    def detener(self):
        self.activo = False
    
    def spawn_avatar(self):
        col = random.randint(0, self.grid_cols - 1)
        posicion = [col, 8]
        TipoAvatar = self.seleccionar_tipo_avatar()
        avatar = TipoAvatar(posicion=posicion)
        self.avatares.append(avatar)
        self.avatares_spawneados += 1
        print(f"   👾 Spawn #{self.avatares_spawneados}: {avatar.nombre} en columna {col}")
        return avatar
    
    def update(self, tiempo_actual, torres_grid):
        if not self.activo or self.tiempo_inicio is None:
            return
        
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
        
        if tiempo_transcurrido - self.ultimo_spawn >= self.proximo_spawn:
            self.spawn_avatar()
            self.ultimo_spawn = tiempo_transcurrido
            self.proximo_spawn = self.calcular_tiempo_spawn()
        
        dt = 0.1
        
        for avatar in self.avatares[:]:
            if not avatar.esta_vivo():
                if avatar not in self.avatares:
                    continue
                self.avatares.remove(avatar)
                self.avatares_eliminados += 1
                continue
            
            if avatar.llegó_a_meta:
                if avatar in self.avatares:
                    self.avatares.remove(avatar)
                    self.avatares_llegaron_meta += 1
                continue
            
            torre_en_frente = self.hay_torre_en_frente(avatar, torres_grid)
            acciones = avatar.step(dt, torre_en_frente)
            
            if acciones.atacar and torre_en_frente:
                self.atacar_torre(avatar, torres_grid)
            
            if acciones.mover and not torre_en_frente:
                avatar.mover_hacia_arriba()
    
    def hay_torre_en_frente(self, avatar, torres_grid):
        col, row = avatar.posicion
        if row > 0:
            celda_frente = (row - 1, col)
            return celda_frente in torres_grid and torres_grid[celda_frente].activa
        return False
    
    def atacar_torre(self, avatar, torres_grid):
        col, row = avatar.posicion
        if row > 0:
            celda_frente = (row - 1, col)
            if celda_frente in torres_grid:
                torre = torres_grid[celda_frente]
                if torre.activa:
                    torre.recibir_damage(avatar.ataque)
                    print(f"   💥 {avatar.nombre} ataca torre de {torre.tipo} (-{avatar.ataque} HP) → {torre.vida_actual}/{torre.vida_maxima}")
    
    def verificar_colisiones_proyectiles(self, proyectiles):
        colisiones = []
        gestor_puntos = self.sistema_puntos
        
        for proyectil in proyectiles[:]:
            if not proyectil.activo:
                continue
            
            for avatar in self.avatares[:]:
                if not avatar.esta_vivo():
                    continue
                
                if self.proyectil_colisiona_con_avatar(proyectil, avatar):
                    puntos_ganados = avatar.recibir_daño(proyectil.damage, gestor_puntos)
                    proyectil.desactivar()
                    colisiones.append((proyectil, avatar))
                    estado = "💀 Eliminado" if not avatar.esta_vivo() else f"❤️ {avatar.vida}/{avatar.vida_maxima} HP"
                    puntos_texto = f"(+{puntos_ganados} pts)" if gestor_puntos else ""
                    print(f"   🎯 Proyectil de {proyectil.tipo} impacta a {avatar.nombre} (-{proyectil.damage} HP) {puntos_texto} → {estado}")
                    break
        
        return colisiones
    
    def proyectil_colisiona_con_avatar(self, proyectil, avatar):
        cell_size = 60
        avatar_x = avatar.posicion[0] * cell_size + cell_size // 2
        avatar_y = avatar.posicion[1] * cell_size + cell_size // 2
        dx = proyectil.posicion[0] - avatar_x
        dy = proyectil.posicion[1] - avatar_y
        distancia = math.sqrt(dx * dx + dy * dy)
        return distancia < 30
    
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