"""
ADAPTADOR DE CONTROL PARA AVATARS VS ROOKS
Maneja la conexión con la Raspberry Pi Pico W y traduce inputs del joystick
a comandos del juego.

Protocolo:
- Wi-Fi Access Point: CONTROL_GAMING / control123
- IP fija: 192.168.4.1:5000
- TCP Socket con JSON
- Frecuencia: 20 Hz
"""

import socket
import json
import threading
import time
from typing import Optional, Callable, Dict, Any


class ControlState:
    """Estado actual del control"""
    def __init__(self):
        self.joystick_x = 0          # -100 a 100
        self.joystick_y = 0          # -100 a 100
        self.joystick_dir = 'neutro' # 'arriba', 'abajo', 'izquierda', 'derecha', 'neutro'
        self.joystick_btn = False    # Botón del stick
        
        self.btn_a = False  # Recoger monedas
        self.btn_b = False  # Reservado
        self.btn_c = False  # Torre Arena
        self.btn_d = False  # Torre Roca
        self.btn_e = False  # Torre Agua
        self.btn_f = False  # Torre Fuego
        
        # Estados previos para detectar flancos (press/release)
        self._prev_joystick_btn = False
        self._prev_btn_a = False
        self._prev_btn_b = False
        self._prev_btn_c = False
        self._prev_btn_d = False
        self._prev_btn_e = False
        self._prev_btn_f = False
    
    def update_from_json(self, data: dict):
        """Actualiza el estado desde un mensaje JSON del control"""
        joy = data.get('joystick', {})
        btn = data.get('botones', {})
        
        # Guardar estados previos
        self._prev_joystick_btn = self.joystick_btn
        self._prev_btn_a = self.btn_a
        self._prev_btn_b = self.btn_b
        self._prev_btn_c = self.btn_c
        self._prev_btn_d = self.btn_d
        self._prev_btn_e = self.btn_e
        self._prev_btn_f = self.btn_f
        
        # Actualizar joystick
        self.joystick_x = joy.get('x', 0)
        self.joystick_y = joy.get('y', 0)
        self.joystick_dir = joy.get('direccion', 'neutro')
        self.joystick_btn = joy.get('button', False)
        
        # Actualizar botones
        self.btn_a = btn.get('A', False)
        self.btn_b = btn.get('B', False)
        self.btn_c = btn.get('C', False)
        self.btn_d = btn.get('D', False)
        self.btn_e = btn.get('E', False)
        self.btn_f = btn.get('F', False)
    
    def get_button_press(self, button: str) -> bool:
        """
        Detecta si un botón fue presionado (flanco de subida)
        
        Args:
            button: 'joystick', 'a', 'b', 'c', 'd', 'e', 'f'
        """
        if button == 'joystick':
            return self.joystick_btn and not self._prev_joystick_btn
        elif button == 'a':
            return self.btn_a and not self._prev_btn_a
        elif button == 'b':
            return self.btn_b and not self._prev_btn_b
        elif button == 'c':
            return self.btn_c and not self._prev_btn_c
        elif button == 'd':
            return self.btn_d and not self._prev_btn_d
        elif button == 'e':
            return self.btn_e and not self._prev_btn_e
        elif button == 'f':
            return self.btn_f and not self._prev_btn_f
        return False


class ControlAdapter:
    """
    Adaptador que conecta con la Raspberry Pi Pico W y maneja
    la comunicación con el juego
    """
    
    def __init__(self, ip: str = "192.168.4.1", port: int = 5000):
        self.ip = ip
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        self.state = ControlState()
        self.on_state_update: Optional[Callable[[ControlState], None]] = None
        
        # Logs de conexión
        self.connection_attempts = 0
        self.last_error = None
        
    def connect(self) -> bool:
        """
        Intenta conectar con el control
        
        Returns:
            True si la conexión fue exitosa
        """
        if self.connected:
            return True
        
        try:
            print(f"🎮 Intentando conectar a {self.ip}:{self.port}...")
            self.connection_attempts += 1
            
            # Crear socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # Timeout de 5 segundos
            
            # Conectar
            self.socket.connect((self.ip, self.port))
            self.connected = True
            
            print(f"✅ Control conectado exitosamente")
            print(f"   Red WiFi: CONTROL_GAMING")
            print(f"   IP: {self.ip}:{self.port}")
            
            # Iniciar hilo de recepción
            self.running = True
            self.thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except ConnectionRefusedError:
            self.last_error = "Conexión rechazada"
            print(f"❌ No se pudo conectar al control")
            print(f"   Verifica:")
            print(f"   1. ¿El control está encendido?")
            print(f"   2. ¿Estás conectado al WiFi: CONTROL_GAMING?")
            print(f"   3. ¿La contraseña es: control123?")
            return False
            
        except socket.timeout:
            self.last_error = "Timeout de conexión"
            print(f"❌ Timeout al conectar con el control")
            return False
            
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta del control"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        
        print("🔌 Control desconectado")
    
    def _receive_loop(self):
        """Loop de recepción de datos (ejecuta en thread separado)"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                # Recibir datos
                datos = self.socket.recv(1024).decode('utf-8')
                
                if not datos:
                    print("⚠️ Control cerró la conexión")
                    self.connected = False
                    break
                
                # Agregar al buffer
                buffer += datos
                
                # Procesar líneas completas (JSON terminado en \n)
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    
                    if linea.strip():
                        try:
                            # Parsear JSON
                            estado_json = json.loads(linea)
                            
                            # Actualizar estado
                            self.state.update_from_json(estado_json)
                            
                            # Callback si existe
                            if self.on_state_update:
                                self.on_state_update(self.state)
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Error parseando JSON: {e}")
                
            except socket.timeout:
                continue
                
            except Exception as e:
                if self.running:  # Solo mostrar error si no es un cierre intencional
                    print(f"⚠️ Error en recepción: {e}")
                    self.connected = False
                break
        
        self.connected = False
        print("🔌 Thread de recepción finalizado")
    
    def is_connected(self) -> bool:
        """Retorna True si el control está conectado"""
        return self.connected
    
    def get_state(self) -> ControlState:
        """Obtiene el estado actual del control"""
        return self.state
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la conexión"""
        return {
            'connected': self.connected,
            'attempts': self.connection_attempts,
            'last_error': self.last_error,
            'ip': self.ip,
            'port': self.port
        }


# ══════════════════════════════════════════════════════════════════════
# FUNCIÓN DE PRUEBA
# ══════════════════════════════════════════════════════════════════════

def test_control():
    """Función de prueba del adaptador"""
    print("\n" + "="*60)
    print("🎮 TEST DEL ADAPTADOR DE CONTROL")
    print("="*60)
    
    adapter = ControlAdapter()
    
    def on_update(state: ControlState):
        """Callback de actualización de estado"""
        messages = []
        
        # Joystick
        if state.joystick_dir != 'neutro':
            messages.append(f"🕹️ Joystick: {state.joystick_dir.upper()}")
        
        # Botón del stick
        if state.get_button_press('joystick'):
            messages.append("🎯 ¡COLOCAR TORRE!")
        
        # Botones
        if state.get_button_press('a'):
            messages.append("💰 Recoger monedas")
        if state.get_button_press('c'):
            messages.append("⛰️ Torre Arena")
        if state.get_button_press('d'):
            messages.append("🪨 Torre Roca")
        if state.get_button_press('e'):
            messages.append("💧 Torre Agua")
        if state.get_button_press('f'):
            messages.append("🔥 Torre Fuego")
        
        if messages:
            print(" | ".join(messages))
    
    adapter.on_state_update = on_update
    
    if adapter.connect():
        print("\n✅ Conexión exitosa")
        print("Presiona CTRL+C para salir\n")
        
        try:
            while adapter.is_connected():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n🛑 Test detenido por el usuario")
    else:
        print("\n❌ No se pudo conectar")
        print("\n💡 INSTRUCCIONES:")
        print("   1. Enciende el control (Raspberry Pi Pico W)")
        print("   2. Conecta tu PC al WiFi: CONTROL_GAMING")
        print("   3. Usa la contraseña: control123")
        print("   4. Ejecuta este script de nuevo")
    
    adapter.disconnect()
    print("\n✅ Test finalizado")


if __name__ == "__main__":
    test_control()