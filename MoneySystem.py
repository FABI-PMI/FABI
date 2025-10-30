"""
Sistema de Puntos y Monedas para Avatars vs Rooks
Incluye: tracking de puntos, spawning de monedas con distribución exponencial
y agrupación aleatoria de monedas
"""
import random
import time
import math


class Moneda:
    """Representa una moneda en el mapa"""
    
    def __init__(self, posicion, valor=10):
        """
        Args:
            posicion: [col, row] en el grid
            valor: valor de la moneda (10, 20, 30, 50)
        """
        self.posicion = list(posicion)  # [col, row]
        self.valor = valor
        self.activa = True
        self.tiempo_spawn = time.time()
        self.tiempo_vida = 15.0  # Moneda desaparece después de 15 segundos
        
        # Configuración visual según valor
        self.config_visual = {
            10: {'icono': '💰', 'color': '#FFD700', 'size': 15},
            20: {'icono': '💎', 'color': '#00CED1', 'size': 18},
            30: {'icono': '🪙', 'color': '#FFA500', 'size': 20},
            50: {'icono': '💵', 'color': '#32CD32', 'size': 22}
        }
        
        self.visual = self.config_visual.get(valor, self.config_visual[10])
    
    def esta_activa(self, tiempo_actual):
        """Verifica si la moneda sigue activa"""
        if not self.activa:
            return False
        
        # Verificar tiempo de vida
        tiempo_transcurrido = tiempo_actual - self.tiempo_spawn
        if tiempo_transcurrido > self.tiempo_vida:
            self.activa = False
            return False
        
        return True
    
    def recolectar(self):
        """Recolecta la moneda"""
        self.activa = False
        return self.valor
    
    def get_icono(self):
        return self.visual['icono']
    
    def get_color(self):
        return self.visual['color']
    
    def get_size(self):
        return self.visual['size']


class GrupoMonedas:
    """Representa un grupo de monedas que spawnean juntas"""
    
    def __init__(self, cantidad, valor_individual, posiciones):
        """
        Args:
            cantidad: número de monedas en el grupo
            valor_individual: valor de cada moneda
            posiciones: lista de [col, row] donde aparecen las monedas
        """
        self.cantidad = cantidad
        self.valor_individual = valor_individual
        self.valor_total = cantidad * valor_individual
        self.monedas = []
        
        # Crear las monedas
        for pos in posiciones[:cantidad]:
            self.monedas.append(Moneda(pos, valor_individual))
    
    def get_monedas_activas(self, tiempo_actual):
        """Retorna las monedas activas del grupo"""
        return [m for m in self.monedas if m.esta_activa(tiempo_actual)]


class SistemaMonedas:
    """Gestiona el spawning y recolección de monedas"""
    
    def __init__(self, grid_cols=5, grid_rows=9):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.monedas_activas = []
        self.grupos_spawneados = []
        
        # Configuración de distribuciones posibles
        # Formato: (cantidad_monedas, valor_individual)
        self.distribuciones_100 = [
            # 100 = suma total
            [(3, 30), (1, 10)],           # 3x30 + 1x10 = 100
            [(2, 30), (2, 20)],           # 2x30 + 2x20 = 100
            [(2, 30), (4, 10)],           # 2x30 + 4x10 = 100
            [(1, 50), (1, 30), (2, 10)],  # 1x50 + 1x30 + 2x10 = 100
            [(2, 50)],                    # 2x50 = 100
            [(5, 20)],                    # 5x20 = 100
            [(10, 10)],                   # 10x10 = 100
            [(1, 50), (2, 20), (1, 10)],  # 1x50 + 2x20 + 1x10 = 100
            [(3, 20), (4, 10)],           # 3x20 + 4x10 = 100
            [(1, 30), (2, 20), (3, 10)]   # 1x30 + 2x20 + 3x10 = 100
        ]
        
        # Configuración exponencial para posiciones
        self.lambda_pos = 0.3
    
    def generar_distribucion_100(self):
        """Genera una distribución aleatoria que suma 100 monedas"""
        return random.choice(self.distribuciones_100)
    
    def generar_posiciones_exponenciales(self, cantidad_total):
        """
        Genera posiciones aleatorias usando distribución exponencial
        para concentrar monedas en ciertas áreas
        """
        posiciones = []
        
        # Generar centro del cluster con distribución exponencial
        centro_col = random.randint(0, self.grid_cols - 1)
        centro_row = random.randint(1, self.grid_rows - 2)  # No en bordes
        
        for i in range(cantidad_total):
            # Intentar generar posición cercana al centro usando exponencial
            intentos = 0
            max_intentos = 20
            
            while intentos < max_intentos:
                # Distancia exponencial desde el centro
                distancia = random.expovariate(self.lambda_pos)
                distancia = min(distancia, 3.0)  # Limitar distancia máxima
                
                # Ángulo aleatorio
                angulo = random.uniform(0, 2 * math.pi)
                
                # Calcular nueva posición
                delta_col = int(distancia * math.cos(angulo))
                delta_row = int(distancia * math.sin(angulo))
                
                nueva_col = centro_col + delta_col
                nueva_row = centro_row + delta_row
                
                # Verificar que esté dentro del grid
                if 0 <= nueva_col < self.grid_cols and 1 <= nueva_row < self.grid_rows - 1:
                    pos = [nueva_col, nueva_row]
                    
                    # Verificar que no esté muy cerca de otra moneda
                    muy_cerca = False
                    for pos_existente in posiciones:
                        dist = math.sqrt(
                            (pos[0] - pos_existente[0])**2 + 
                            (pos[1] - pos_existente[1])**2
                        )
                        if dist < 0.5:  # Muy cerca
                            muy_cerca = True
                            break
                    
                    if not muy_cerca:
                        posiciones.append(pos)
                        break
                
                intentos += 1
            
            # Si no se pudo encontrar posición cercana, usar una aleatoria
            if intentos >= max_intentos:
                col = random.randint(0, self.grid_cols - 1)
                row = random.randint(1, self.grid_rows - 2)
                posiciones.append([col, row])
        
        return posiciones
    
    def spawnear_monedas_100(self):
        """Spawnea un conjunto de monedas que suman $100"""
        # Seleccionar distribución
        distribucion = self.generar_distribucion_100()
        
        print(f"\n💰 SPAWNING DE MONEDAS - $100")
        print(f"   Distribución: {distribucion}")
        
        # Calcular cantidad total de monedas
        cantidad_total = sum(cant for cant, _ in distribucion)
        
        # Generar posiciones
        posiciones = self.generar_posiciones_exponenciales(cantidad_total)
        
        # Crear grupos de monedas
        idx_pos = 0
        for cantidad, valor in distribucion:
            # Obtener posiciones para este grupo
            posiciones_grupo = posiciones[idx_pos:idx_pos + cantidad]
            idx_pos += cantidad
            
            # Crear grupo
            grupo = GrupoMonedas(cantidad, valor, posiciones_grupo)
            self.grupos_spawneados.append(grupo)
            
            # Agregar monedas a la lista activa
            self.monedas_activas.extend(grupo.monedas)
            
            print(f"   → {cantidad}x ${valor} = ${cantidad * valor}")
        
        print(f"   Total de monedas spawneadas: {cantidad_total}")
        print(f"   Valor total: $100\n")
    
    def update(self, tiempo_actual):
        """Actualiza el estado de las monedas"""
        # Limpiar monedas inactivas
        self.monedas_activas = [
            m for m in self.monedas_activas 
            if m.esta_activa(tiempo_actual)
        ]
    
    def intentar_recolectar(self, posicion_click_col, posicion_click_row):
        """
        Intenta recolectar una moneda en la posición clickeada
        Retorna el valor de la moneda si se recolectó, 0 si no
        """
        for moneda in self.monedas_activas:
            if moneda.posicion[0] == posicion_click_col and \
               moneda.posicion[1] == posicion_click_row and \
               moneda.activa:
                valor = moneda.recolectar()
                print(f"   💰 ¡Moneda recolectada! +${valor}")
                return valor
        
        return 0
    
    def get_monedas_activas(self, tiempo_actual):
        """Retorna lista de monedas activas"""
        self.update(tiempo_actual)
        return self.monedas_activas
    
    def limpiar_todo(self):
        """Limpia todas las monedas"""
        self.monedas_activas.clear()
        self.grupos_spawneados.clear()


class SistemaPuntos:
    """Gestiona el sistema de puntos del juego"""
    
    def __init__(self):
        self.puntos_totales = 0
        self.puntos_desde_ultimo_spawn = 0
        self.puntos_para_spawn = 30  # Cada 30 puntos spawn $100 en monedas
        
        self.sistema_monedas = None  # Se asigna externamente
        
        # Estadísticas
        self.puntos_por_flechador = 0
        self.puntos_por_escudero = 0
        self.puntos_por_leñador = 0
        self.puntos_por_canibal = 0
        
        self.spawns_monedas = 0
        self.dinero_spawneado = 0
    
    def agregar_puntos(self, puntos, tipo_avatar=None):
        """
        Agrega puntos al sistema
        Args:
            puntos: cantidad de puntos (= vida quitada)
            tipo_avatar: nombre del avatar para estadísticas
        """
        self.puntos_totales += puntos
        self.puntos_desde_ultimo_spawn += puntos
        
        # Actualizar estadísticas por tipo
        if tipo_avatar:
            if tipo_avatar == "Flechador":
                self.puntos_por_flechador += puntos
            elif tipo_avatar == "Escudero":
                self.puntos_por_escudero += puntos
            elif tipo_avatar == "Leñador":
                self.puntos_por_leñador += puntos
            elif tipo_avatar == "Caníbal":
                self.puntos_por_canibal += puntos
        
        # Verificar si es momento de spawnear monedas
        if self.puntos_desde_ultimo_spawn >= self.puntos_para_spawn:
            self.spawnear_monedas()
            self.puntos_desde_ultimo_spawn -= self.puntos_para_spawn
    
    def spawnear_monedas(self):
        """Spawnea $100 en monedas cuando se alcanzan 30 puntos"""
        if self.sistema_monedas:
            self.sistema_monedas.spawnear_monedas_100()
            self.spawns_monedas += 1
            self.dinero_spawneado += 100
            
            print(f"🎉 ¡30 PUNTOS ALCANZADOS! Spawning $100 en monedas")
            print(f"   Puntos totales: {self.puntos_totales}")
            print(f"   Spawns de monedas: {self.spawns_monedas}")
    
    def get_progreso_spawn(self):
        """Retorna el progreso hacia el siguiente spawn (0.0 - 1.0)"""
        return min(1.0, self.puntos_desde_ultimo_spawn / self.puntos_para_spawn)
    
    def get_estadisticas(self):
        """Retorna diccionario con estadísticas"""
        return {
            'puntos_totales': self.puntos_totales,
            'puntos_para_spawn': self.puntos_desde_ultimo_spawn,
            'progreso_spawn': self.get_progreso_spawn(),
            'spawns_monedas': self.spawns_monedas,
            'dinero_spawneado': self.dinero_spawneado,
            'por_flechador': self.puntos_por_flechador,
            'por_escudero': self.puntos_por_escudero,
            'por_leñador': self.puntos_por_leñador,
            'por_canibal': self.puntos_por_canibal
        }
    
    def reset(self):
        """Reinicia el sistema de puntos"""
        self.puntos_totales = 0
        self.puntos_desde_ultimo_spawn = 0
        self.puntos_por_flechador = 0
        self.puntos_por_escudero = 0
        self.puntos_por_leñador = 0
        self.puntos_por_canibal = 0
        self.spawns_monedas = 0
        self.dinero_spawneado = 0


# ===== FUNCIONES DE UTILIDAD =====

def calcular_puntos_por_daño(daño, vida_avatar):
    """
    Calcula los puntos obtenidos por hacer daño a un avatar
    1 punto = 1 HP de daño
    """
    return min(daño, vida_avatar)  # No dar más puntos de los que tiene de vida


def verificar_distribuciones():
    """Función de prueba para verificar que todas las distribuciones suman 100"""
    sistema = SistemaMonedas()
    
    print("🔍 VERIFICACIÓN DE DISTRIBUCIONES")
    print("="*50)
    
    todas_correctas = True
    for i, dist in enumerate(sistema.distribuciones_100, 1):
        total = sum(cant * valor for cant, valor in dist)
        check = "✅" if total == 100 else "❌"
        print(f"{check} Distribución {i}: {dist} = ${total}")
        
        if total != 100:
            todas_correctas = False
    
    print("="*50)
    if todas_correctas:
        print("✅ Todas las distribuciones son correctas!")
    else:
        print("❌ Hay distribuciones incorrectas!")
    
    return todas_correctas


if __name__ == "__main__":
    # Pruebas del sistema
    print("\n" + "="*60)
    print(" "*15 + "PRUEBA DEL SISTEMA DE MONEDAS")
    print("="*60 + "\n")
    
    # Verificar distribuciones
    verificar_distribuciones()
    
    # Prueba de spawning
    print("\n" + "="*60)
    print("PRUEBA DE SPAWNING")
    print("="*60)
    
    sistema_monedas = SistemaMonedas(grid_cols=5, grid_rows=9)
    sistema_puntos = SistemaPuntos()
    sistema_puntos.sistema_monedas = sistema_monedas
    
    # Simular daño a avatares
    print("\n🎮 Simulando combate...")
    print("-"*60)
    
    # Flechador recibe 5 de daño (muere)
    print("\n🏹 Flechador recibe 5 de daño")
    sistema_puntos.agregar_puntos(5, "Flechador")
    
    # Escudero recibe 7 de daño
    print("\n🛡️ Escudero recibe 7 de daño")
    sistema_puntos.agregar_puntos(7, "Escudero")
    
    # Flechador recibe 3 de daño
    print("\n🏹 Otro Flechador recibe 3 de daño")
    sistema_puntos.agregar_puntos(3, "Flechador")
    
    # Leñador recibe 15 de daño
    print("\n🪓 Leñador recibe 15 de daño")
    sistema_puntos.agregar_puntos(15, "Leñador")
    
    # Esto debería triggear el spawn (5+7+3+15 = 30)
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS FINALES")
    print("="*60)
    
    stats = sistema_puntos.get_estadisticas()
    print(f"\n📊 Puntos Totales: {stats['puntos_totales']}")
    print(f"💰 Spawns de Monedas: {stats['spawns_monedas']}")
    print(f"💵 Dinero Total Spawneado: ${stats['dinero_spawneado']}")
    print(f"\n🎯 Puntos por tipo:")
    print(f"   🏹 Flechador: {stats['por_flechador']}")
    print(f"   🛡️ Escudero: {stats['por_escudero']}")
    print(f"   🪓 Leñador: {stats['por_leñador']}")
    print(f"   👹 Caníbal: {stats['por_canibal']}")
    
    print(f"\n🔄 Progreso hacia siguiente spawn: {stats['puntos_para_spawn']}/30 " +
          f"({stats['progreso_spawn']*100:.1f}%)")
    
    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA")
    print("="*60 + "\n")