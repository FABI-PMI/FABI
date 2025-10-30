import time
import math

class Proyectil:
    """Clase para los proyectiles disparados por las torres"""
    def __init__(self, posicion, velocidad, damage, color, tipo):
        self.posicion = list(posicion)  # [x, y] en píxeles
        self.velocidad = velocidad
        self.damage = damage
        self.color = color
        self.tipo = tipo
        self.activo = True
        self.direccion = [0, 1]  # DIRECCIÓN HACIA ABAJO (y positivo)
    
    def actualizar(self, dt):
        """Actualiza la posición del proyectil"""
        if self.activo:
            self.posicion[0] += self.direccion[0] * self.velocidad * dt
            self.posicion[1] += self.direccion[1] * self.velocidad * dt
    
    def esta_fuera_pantalla(self, altura_pantalla=750):
        """Verifica si el proyectil salió de la pantalla"""
        return self.posicion[1] > altura_pantalla or self.posicion[1] < 0
    
    def desactivar(self):
        """Desactiva el proyectil"""
        self.activo = False


class Rook:
    """Clase base para todas las torres"""
    def __init__(self, tipo, vida, frecuencia_disparo, damage_proyectil, color_proyectil):
        self.tipo = tipo
        self.vida_maxima = vida
        self.vida_actual = vida
        self.frecuencia_disparo = frecuencia_disparo
        self.damage_proyectil = damage_proyectil
        self.color_proyectil = color_proyectil
        self.activa = True
        self.ultimo_disparo = 0
        self.proyectiles = []
    
    def disparar(self, tiempo_actual, posicion_torre):
        """
        Dispara un proyectil hacia abajo si ha pasado suficiente tiempo
        posicion_torre: [x, y] en píxeles de la posición de la torre
        """
        if not self.activa:
            return None
        
        tiempo_desde_ultimo = tiempo_actual - self.ultimo_disparo
        
        if tiempo_desde_ultimo >= self.frecuencia_disparo:
            self.ultimo_disparo = tiempo_actual
            
            # Crear proyectil en la posición de la torre
            proyectil = Proyectil(
                posicion=posicion_torre.copy(),
                velocidad=300,
                damage=self.damage_proyectil,
                color=self.color_proyectil,
                tipo=self.tipo
            )
            
            self.proyectiles.append(proyectil)
            print(f"   🎯 Torre {self.tipo} disparó desde posición {posicion_torre}")
            return proyectil
        
        return None
    
    def actualizar_proyectiles(self, dt):
        """✅ CORREGIDO: Limpia proyectiles desactivados inmediatamente"""
        for proyectil in self.proyectiles[:]:
            if not proyectil.activo:
                self.proyectiles.remove(proyectil)
                continue
            
            proyectil.actualizar(dt)
            
            if proyectil.esta_fuera_pantalla():
                proyectil.desactivar()
                self.proyectiles.remove(proyectil)
    
    def recibir_damage(self, damage):
        """La torre recibe daño"""
        self.vida_actual = max(0, self.vida_actual - damage)
        if self.vida_actual <= 0:
            self.activa = False
            print(f"   💥 Torre de {self.tipo} destruida!")
    
    def esta_viva(self):
        """Verifica si la torre sigue activa"""
        return self.activa and self.vida_actual > 0


class RookArena(Rook):
    """Torre de Arena - Disparo rápido, poco daño"""
    def __init__(self):
        super().__init__(
            tipo="Arena",
            vida=15,
            frecuencia_disparo=1.0,
            damage_proyectil=2,
            color_proyectil="#D2B48C"
        )
        self.color = "#DEB887"
        self.icono = "⛰️"


class RookRoca(Rook):
    """Torre de Roca - Resistente, disparo medio"""
    def __init__(self):
        super().__init__(
            tipo="Roca",
            vida=30,
            frecuencia_disparo=2.0,
            damage_proyectil=4,
            color_proyectil="#808080"
        )
        self.color = "#696969"
        self.icono = "🪨"


class RookAgua(Rook):
    """Torre de Agua - Daño medio, velocidad media"""
    def __init__(self):
        super().__init__(
            tipo="Agua",
            vida=20,
            frecuencia_disparo=1.5,
            damage_proyectil=3,
            color_proyectil="#4169E1"
        )
        self.color = "#4682B4"
        self.icono = "💧"


class RookFuego(Rook):
    """Torre de Fuego - Mucho daño, lenta"""
    def __init__(self):
        super().__init__(
            tipo="Fuego",
            vida=20,
            frecuencia_disparo=3.0,
            damage_proyectil=6,
            color_proyectil="#FF4500"
        )
        self.color = "#FF4500"
        self.icono = "🔥"


class GestorRooks:
    """Gestiona todas las torres del juego"""
    def __init__(self):
        self.torres = {}  # Diccionario {(row, col): Rook}
        self.tipos_disponibles = {
            "Arena": RookArena,
            "Roca": RookRoca,
            "Agua": RookAgua,
            "Fuego": RookFuego
        }
    
    def agregar_torre(self, tipo, row, col):
        """Agrega una torre en la posición especificada"""
        if (row, col) in self.torres:
            print(f"   ⚠️ Ya existe una torre en ({row}, {col})")
            return False
        
        if tipo not in self.tipos_disponibles:
            print(f"   ⚠️ Tipo de torre desconocido: {tipo}")
            return False
        
        torre = self.tipos_disponibles[tipo]()
        self.torres[(row, col)] = torre
        print(f"   ✅ Torre de {tipo} colocada en ({row}, {col})")
        return True
    
    def actualizar(self, dt, tiempo_actual, grid_config):
        """
        ✅ CORREGIDO: Limpia torres destruidas ANTES de disparar
        """
        # ✅ CAMBIO 2: Primero limpiar torres destruidas
        torres_a_eliminar = []
        for pos, torre in list(self.torres.items()):
            if not torre.esta_viva() or not torre.activa:
                torres_a_eliminar.append(pos)
        
        for pos in torres_a_eliminar:
            del self.torres[pos]
            print(f"   🗑️ Torre eliminada de posición {pos}")
        
        # Ahora actualizar torres vivas
        for (row, col), torre in list(self.torres.items()):
            if not torre.esta_viva():
                continue
            
            # Calcular posición en píxeles de la torre
            x = grid_config['x'] + col * grid_config['cell_size'] + grid_config['cell_size'] // 2
            y = grid_config['y'] + row * grid_config['cell_size'] + grid_config['cell_size'] // 2
            posicion_torre = [x, y]
            
            # Disparar hacia abajo automáticamente según frecuencia
            torre.disparar(tiempo_actual, posicion_torre)
            
            # Actualizar proyectiles
            torre.actualizar_proyectiles(dt)
    
    def get_todos_proyectiles(self):
        """Retorna todos los proyectiles activos de todas las torres"""
        proyectiles = []
        for torre in self.torres.values():
            proyectiles.extend([p for p in torre.proyectiles if p.activo])
        return proyectiles
    
    def eliminar_torres_destruidas(self):
        """Elimina torres que ya no están activas"""
        torres_a_eliminar = []
        for pos, torre in self.torres.items():
            if not torre.activa:
                torres_a_eliminar.append(pos)
        
        for pos in torres_a_eliminar:
            del self.torres[pos]
    
    def actualizar_frecuencias(self, frecuencias_dict):
        """Actualiza las frecuencias de disparo desde el menú"""
        mapeo = {
            "⛰️  TORRE DE ARENA": "Arena",
            "🪨  TORRE DE ROCA": "Roca",
            "💧 TORRE DE AGUA": "Agua",
            "🔥 TORRE DE FUEGO": "Fuego"
        }
        
        for nombre_menu, frecuencia in frecuencias_dict.items():
            tipo = mapeo.get(nombre_menu)
            if tipo:
                for torre in self.torres.values():
                    if torre.tipo == tipo:
                        torre.frecuencia_disparo = frecuencia