import time

class Proyectil:
    """Clase base para los proyectiles que disparan las torres"""
    
    def __init__(self, tipo, damage, velocidad, posicion_inicial):
        self.tipo = tipo
        self.damage = damage
        self.velocidad = velocidad  # Pixels por frame
        self.posicion = list(posicion_inicial)  # [x, y]
        self.activo = True
        
    def mover(self):
        """Mueve el proyectil hacia adelante (derecha)"""
        if self.activo:
            self.posicion[0] += self.velocidad
    
    def colisiona_con(self, objetivo):
        """Verifica colisión con un objetivo (avatar enemigo)"""
        # Implementar lógica de colisión según tu sistema de coordenadas
        pass
    
    def desactivar(self):
        """Desactiva el proyectil cuando impacta o sale de pantalla"""
        self.activo = False


class ProyectilArena(Proyectil):
    def __init__(self, posicion_inicial):
        super().__init__(
            tipo="Arena",
            damage=4,
            velocidad=8,
            posicion_inicial=posicion_inicial
        )
        self.color = "#C4A35A"
        self.efecto = "ralentizar"  # Efecto especial de arena


class ProyectilRoca(Proyectil):
    def __init__(self, posicion_inicial):
        super().__init__(
            tipo="Roca",
            damage=6,
            velocidad=6,
            posicion_inicial=posicion_inicial
        )
        self.color = "#7A6F5D"
        self.efecto = "aturdimiento"  # Efecto especial de roca


class ProyectilAgua(Proyectil):
    def __init__(self, posicion_inicial):
        super().__init__(
            tipo="Agua",
            damage=10,
            velocidad=10,
            posicion_inicial=posicion_inicial
        )
        self.color = "#5B7C8D"
        self.efecto = "penetracion"  # Atraviesa múltiples enemigos


class ProyectilFuego(Proyectil):
    def __init__(self, posicion_inicial):
        super().__init__(
            tipo="Fuego",
            damage=8,
            velocidad=12,
            posicion_inicial=posicion_inicial
        )
        self.color = "#B85450"
        self.efecto = "quemadura"  # Daño continuo


class Rook:
    """Clase base para todas las torres"""
    
    def __init__(self, tipo, vida, precio, damage_proyectil, posicion, frecuencia_disparo=5):
        self.tipo = tipo
        self.vida_maxima = vida
        self.vida_actual = vida
        self.precio = precio
        self.damage_proyectil = damage_proyectil
        self.posicion = posicion  # [x, y] en el grid
        self.frecuencia_disparo = frecuencia_disparo  # 0-10 del slider
        self.ultimo_disparo = 0
        self.proyectiles = []
        self.activa = True
        self.nivel = 1
        
    def puede_disparar(self, tiempo_actual):
        """Verifica si la torre puede disparar según su frecuencia"""
        # La frecuencia indica cada cuántos segundos dispara
        # Frecuencia 5 = dispara cada 5 segundos
        # Frecuencia 10 = dispara cada 10 segundos
        # Frecuencia 1 = dispara cada 1 segundo
        cooldown = self.frecuencia_disparo
        return (tiempo_actual - self.ultimo_disparo) >= cooldown
    
    def disparar(self, tiempo_actual):
        """Crea un nuevo proyectil si puede disparar"""
        if self.puede_disparar(tiempo_actual) and self.activa:
            proyectil = self.crear_proyectil()
            self.proyectiles.append(proyectil)
            self.ultimo_disparo = tiempo_actual
            return proyectil
        return None
    
    def crear_proyectil(self):
        """Método a sobrescribir por cada subclase"""
        raise NotImplementedError("Cada torre debe implementar crear_proyectil()")
    
    def recibir_damage(self, damage):
        """Reduce la vida de la torre"""
        self.vida_actual -= damage
        if self.vida_actual <= 0:
            self.vida_actual = 0
            self.destruir()
    
    def reparar(self, cantidad):
        """Repara la torre (no puede exceder vida máxima)"""
        self.vida_actual = min(self.vida_actual + cantidad, self.vida_maxima)
    
    def destruir(self):
        """Destruye la torre"""
        self.activa = False
    
    def mejorar(self):
        """Mejora la torre (aumenta stats)"""
        self.nivel += 1
        self.vida_maxima = int(self.vida_maxima * 1.2)
        self.vida_actual = self.vida_maxima
        self.damage_proyectil = int(self.damage_proyectil * 1.15)
    
    def actualizar_frecuencia(self, nueva_frecuencia):
        """Actualiza la frecuencia de disparo desde el menú"""
        self.frecuencia_disparo = nueva_frecuencia
    
    def get_info(self):
        """Retorna información de la torre"""
        return {
            'tipo': self.tipo,
            'vida': f"{self.vida_actual}/{self.vida_maxima}",
            'nivel': self.nivel,
            'frecuencia': self.frecuencia_disparo,
            'precio': self.precio,
            'damage': self.damage_proyectil
        }


class RookArena(Rook):
    """🏜️ Torre de Arena - Barata y rápida pero débil"""
    
    def __init__(self, posicion, frecuencia_disparo=5):
        super().__init__(
            tipo="Arena",
            vida=10,
            precio=50,
            damage_proyectil=4,
            posicion=posicion,
            frecuencia_disparo=frecuencia_disparo
        )
        self.color = "#C4A35A"
        self.icono = "⛰️"
        
    def crear_proyectil(self):
        return ProyectilArena(self.posicion.copy())


class RookRoca(Rook):
    """🪨 Torre de Roca - Resistente y equilibrada"""
    
    def __init__(self, posicion, frecuencia_disparo=5):
        super().__init__(
            tipo="Roca",
            vida=14,
            precio=100,
            damage_proyectil=6,
            posicion=posicion,
            frecuencia_disparo=frecuencia_disparo
        )
        self.color = "#7A6F5D"
        self.icono = "🪨"
        
    def crear_proyectil(self):
        return ProyectilRoca(self.posicion.copy())


class RookAgua(Rook):
    """💧 Torre de Agua - Potente y veloz pero cara"""
    
    def __init__(self, posicion, frecuencia_disparo=5):
        super().__init__(
            tipo="Agua",
            vida=16,
            precio=150,
            damage_proyectil=10,
            posicion=posicion,
            frecuencia_disparo=frecuencia_disparo
        )
        self.color = "#5B7C8D"
        self.icono = "💧"
        
    def crear_proyectil(self):
        return ProyectilAgua(self.posicion.copy())


class RookFuego(Rook):
    """🔥 Torre de Fuego - Alto daño con efecto continuo"""
    
    def __init__(self, posicion, frecuencia_disparo=5):
        super().__init__(
            tipo="Fuego",
            vida=16,
            precio=150,
            damage_proyectil=8,
            posicion=posicion,
            frecuencia_disparo=frecuencia_disparo
        )
        self.color = "#B85450"
        self.icono = "🔥"
        
    def crear_proyectil(self):
        return ProyectilFuego(self.posicion.copy())


# ===== SISTEMA DE GESTIÓN DE TORRES =====

class GestorRooks:
    """Gestiona todas las torres en el juego"""
    
    def __init__(self):
        self.torres = []
        self.proyectiles_activos = []
        
    def agregar_torre(self, tipo_torre, posicion, frecuencia=5):
        """Crea y agrega una nueva torre"""
        tipos = {
            "Arena": RookArena,
            "Roca": RookRoca,
            "Agua": RookAgua,
            "Fuego": RookFuego
        }
        
        if tipo_torre in tipos:
            torre = tipos[tipo_torre](posicion, frecuencia)
            self.torres.append(torre)
            return torre
        return None
    
    def actualizar_frecuencias(self, frecuencias_dict):
        """
        Actualiza las frecuencias de todas las torres desde el menú
        frecuencias_dict: diccionario del método get_all_frequencies() del menú
        """
        mapeo = {
            "⛰️  TORRE DE ARENA": "Arena",
            "🪨  TORRE DE ROCA": "Roca",
            "💧 TORRE DE AGUA": "Agua",
            "🔥 TORRE DE FUEGO": "Fuego"
        }
        
        for nombre_menu, frecuencia in frecuencias_dict.items():
            tipo = mapeo.get(nombre_menu)
            if tipo:
                for torre in self.torres:
                    if torre.tipo == tipo:
                        torre.actualizar_frecuencia(frecuencia)
    
    def update(self, tiempo_actual):
        """Actualiza todas las torres y proyectiles"""
        # Disparar desde todas las torres activas
        for torre in self.torres:
            if torre.activa:
                proyectil = torre.disparar(tiempo_actual)
                if proyectil:
                    self.proyectiles_activos.append(proyectil)
        
        # Actualizar proyectiles
        for proyectil in self.proyectiles_activos[:]:
            proyectil.mover()
            
            # Remover proyectiles inactivos o fuera de pantalla
            if not proyectil.activo or proyectil.posicion[0] > 1200:
                self.proyectiles_activos.remove(proyectil)
    
    def eliminar_torres_destruidas(self):
        """Limpia torres destruidas de la lista"""
        self.torres = [t for t in self.torres if t.activa]
    
    def get_torres_activas(self):
        """Retorna lista de torres activas"""
        return [t for t in self.torres if t.activa]
