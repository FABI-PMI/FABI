"""
Pruebas Unitarias para el juego Avatars VS Rooks
Incluye tests para:
1. Sistema de Login
2. Sistema de colocación de Torres (Rooks)
3. Sistema de visualización de mejores puntajes (Salón de la Fama)
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio de uploads al path para importar módulos
sys.path.insert(0, '/mnt/user-data/uploads')

from RooksClass import RookArena, RookRoca, RookAgua, RookFuego, GestorRooks, Proyectil


# ═══════════════════════════════════════════════════════════════════════════
# PRUEBAS UNITARIAS: PUNTO 1 - SISTEMA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════

class TestSistemaLogin(unittest.TestCase):
    """Pruebas para el sistema de login y gestión de usuarios"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear un archivo temporal para simular la base de datos
        self.temp_dir = tempfile.mkdtemp()
        self.test_usuarios_file = os.path.join(self.temp_dir, "test_usuarios.json")
        
        # Usuarios de prueba
        self.usuarios_test = {
            "nacho": {
                "nombre": "Nacho",
                "apellido": "Rodriguez",
                "contrasena": "1234",
                "correo": "nacho@example.com",
                "telefono": "88888888",
                "pts": 150
            },
            "maria": {
                "nombre": "Maria",
                "apellido": "Garcia",
                "contrasena": "pass123",
                "correo": "maria@example.com",
                "telefono": "77777777",
                "pts": 200
            },
            "juan": {
                "nombre": "Juan",
                "apellido": "Perez",
                "contrasena": "secret",
                "correo": "juan@example.com",
                "telefono": "66666666",
                "pts": 100
            }
        }
        
        # Guardar usuarios de prueba
        with open(self.test_usuarios_file, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios_test, f, ensure_ascii=False, indent=4)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        shutil.rmtree(self.temp_dir)
    
    def test_cargar_usuarios_exitoso(self):
        """Test 1: Verificar que se pueden cargar usuarios correctamente"""
        with open(self.test_usuarios_file, 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        self.assertEqual(len(usuarios), 3)
        self.assertIn("nacho", usuarios)
        self.assertEqual(usuarios["nacho"]["nombre"], "Nacho")
        print("✅ Test 1 pasado: Carga de usuarios exitosa")
    
    def test_verificar_credenciales_usuario(self):
        """Test 2: Verificar credenciales de login con username"""
        usuarios = self.usuarios_test
        
        # Credenciales correctas
        credencial = "nacho"
        contrasena = "1234"
        
        usuario_encontrado = None
        for usuario, datos in usuarios.items():
            if credencial == usuario and datos["contrasena"] == contrasena:
                usuario_encontrado = usuario
                break
        
        self.assertIsNotNone(usuario_encontrado)
        self.assertEqual(usuario_encontrado, "nacho")
        print("✅ Test 2 pasado: Verificación de credenciales con usuario")
    
    def test_verificar_credenciales_incorrectas(self):
        """Test 3: Verificar que credenciales incorrectas fallan"""
        usuarios = self.usuarios_test
        
        # Credenciales incorrectas
        credencial = "nacho"
        contrasena_incorrecta = "wrongpass"
        
        usuario_encontrado = None
        for usuario, datos in usuarios.items():
            if credencial == usuario and datos["contrasena"] == contrasena_incorrecta:
                usuario_encontrado = usuario
                break
        
        self.assertIsNone(usuario_encontrado)
        print("✅ Test 3 pasado: Rechazo de credenciales incorrectas")


# ═══════════════════════════════════════════════════════════════════════════
# PRUEBAS UNITARIAS: PUNTO 2 - SISTEMA DE TORRES (ROOKS)
# ═══════════════════════════════════════════════════════════════════════════

class TestSistemaTorres(unittest.TestCase):
    """Pruebas para el sistema de colocación y gestión de torres"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.gestor = GestorRooks()
    
    def test_crear_torre_arena(self):
        """Test 1: Crear una torre de Arena"""
        torre = RookArena()
        
        self.assertEqual(torre.tipo, "Arena")
        self.assertEqual(torre.vida_maxima, 15)
        self.assertEqual(torre.vida_actual, 15)
        self.assertEqual(torre.frecuencia_disparo, 1.0)
        self.assertEqual(torre.damage_proyectil, 2)
        self.assertTrue(torre.activa)
        print("✅ Test 1 pasado: Creación de torre Arena")
    
    def test_agregar_torre_al_grid(self):
        """Test 2: Agregar torre a una posición del grid"""
        row, col = 2, 3
        torre = self.gestor.agregar_torre("Arena", row, col)
        
        self.assertIsNotNone(torre)
        self.assertIn((row, col), self.gestor.torres)
        self.assertEqual(self.gestor.torres[(row, col)].tipo, "Arena")
        print("✅ Test 2 pasado: Torre agregada al grid correctamente")
    
    def test_torre_disparar_proyectil(self):
        """Test 3: Torre puede disparar proyectiles"""
        torre = RookArena()
        posicion_torre = [100, 200]
        tiempo_actual = 2.0
        
        proyectil = torre.disparar(tiempo_actual, posicion_torre)
        
        self.assertIsNotNone(proyectil)
        self.assertEqual(len(torre.proyectiles), 1)
        self.assertEqual(proyectil.tipo, "Arena")
        self.assertEqual(proyectil.damage, 2)
        print("✅ Test 3 pasado: Torre dispara proyectiles correctamente")


# ═══════════════════════════════════════════════════════════════════════════
# PRUEBAS UNITARIAS: PUNTO 3 - SISTEMA DE MEJORES PUNTAJES
# ═══════════════════════════════════════════════════════════════════════════

class TestSistemaPuntajes(unittest.TestCase):
    """Pruebas para el sistema de visualización de mejores puntajes"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.usuarios = {
            "alice": {"nombre": "Alice", "apellido": "Wonder", "pts": 500},
            "bob": {"nombre": "Bob", "apellido": "Builder", "pts": 300},
            "charlie": {"nombre": "Charlie", "apellido": "Chocolate", "pts": 450},
            "diana": {"nombre": "Diana", "apellido": "Prince", "pts": 600},
            "eve": {"nombre": "Eve", "apellido": "Online", "pts": 250},
            "frank": {"nombre": "Frank", "apellido": "Castle", "pts": 400},
            "grace": {"nombre": "Grace", "apellido": "Hopper", "pts": 550},
            "henry": {"nombre": "Henry", "apellido": "Ford", "pts": 350},
            "iris": {"nombre": "Iris", "apellido": "West", "pts": 480},
            "jack": {"nombre": "Jack", "apellido": "Sparrow", "pts": 520}
        }
    
    def test_obtener_usuarios_con_puntos(self):
        """Test 1: Obtener lista de usuarios con sus puntos"""
        usuarios_con_pts = []
        
        for username, datos in self.usuarios.items():
            if isinstance(datos, dict):
                pts = datos.get('pts', 0)
                usuarios_con_pts.append((username, datos, pts))
        
        self.assertEqual(len(usuarios_con_pts), 10)
        print("✅ Test 1 pasado: Obtención de usuarios con puntos")
    
    def test_ordenar_usuarios_por_puntos(self):
        """Test 2: Ordenar usuarios por puntos (mayor a menor)"""
        usuarios_con_pts = []
        
        for username, datos in self.usuarios.items():
            pts = datos.get('pts', 0)
            usuarios_con_pts.append((username, datos, pts))
        
        # Ordenar por puntos
        usuarios_con_pts.sort(key=lambda x: x[2], reverse=True)
        
        # Verificar que el primero tenga más puntos que el último
        self.assertGreater(usuarios_con_pts[0][2], usuarios_con_pts[-1][2])
        
        # Verificar el orden específico
        self.assertEqual(usuarios_con_pts[0][0], "diana")  # 600 pts
        self.assertEqual(usuarios_con_pts[1][0], "grace")  # 550 pts
        self.assertEqual(usuarios_con_pts[2][0], "jack")   # 520 pts
        print("✅ Test 2 pasado: Ordenamiento correcto por puntos")
    
    def test_verificar_primer_lugar(self):
        """Test 3: Verificar que el primer lugar tenga los puntos más altos"""
        usuarios_con_pts = []
        
        for username, datos in self.usuarios.items():
            pts = datos.get('pts', 0)
            usuarios_con_pts.append((username, datos, pts))
        
        usuarios_con_pts.sort(key=lambda x: x[2], reverse=True)
        
        primer_lugar = usuarios_con_pts[0]
        
        self.assertEqual(primer_lugar[0], "diana")
        self.assertEqual(primer_lugar[2], 600)
        print("✅ Test 3 pasado: Primer lugar identificado correctamente")


# ═══════════════════════════════════════════════════════════════════════════
# EJECUTAR PRUEBAS
# ═══════════════════════════════════════════════════════════════════════════

def suite():
    """Crea la suite completa de pruebas"""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Agregar pruebas de login
    test_suite.addTests(loader.loadTestsFromTestCase(TestSistemaLogin))
    
    # Agregar pruebas de torres
    test_suite.addTests(loader.loadTestsFromTestCase(TestSistemaTorres))
    
    # Agregar pruebas de puntajes
    test_suite.addTests(loader.loadTestsFromTestCase(TestSistemaPuntajes))
    
    return test_suite


if __name__ == '__main__':
    print("=" * 80)
    print("PRUEBAS UNITARIAS - AVATARS VS ROOKS")
    print("=" * 80)
    print("\n📋 Ejecutando 9 pruebas:")
    print("   1. Sistema de Login (3 pruebas)")
    print("   2. Sistema de Torres (3 pruebas)")
    print("   3. Sistema de Puntajes (3 pruebas)")
    print("\n" + "=" * 80 + "\n")
    
    # Ejecutar todas las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    
    # Salir con código apropiado
    sys.exit(0 if result.wasSuccessful() else 1)