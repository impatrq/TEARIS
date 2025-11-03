#!/usr/bin/env python3
"""
TEARIS - Control de hardware WM8960 Audio HAT
Este módulo controla el ecualizador y volumen del WM8960 usando ALSA
"""

import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WM8960Controller:
    """
    Controlador para el WM8960 Audio HAT
    Maneja volumen, ecualización y configuración de audio
    """
    
    def __init__(self):
        self.card = 'wm8960soundcard'
        self.current_mode = 'NORMAL'
        logger.info("🎵 Inicializando WM8960 Controller...")
        self.init_safe_config()
    
    def _amixer(self, control, value):
        """
        Ejecuta un comando amixer para controlar el WM8960
        
        Args:
            control: Nombre del control ALSA (ej: 'Headphone', 'EQ1')
            value: Valor a establecer (ej: '60%', '+6', 'on')
        
        Returns:
            bool: True si el comando fue exitoso
        """
        try:
            cmd = ['amixer', '-c', self.card, 'sset', control, str(value)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error configurando {control}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
    
    def init_safe_config(self):
        """
        Configuración inicial segura para hiperacusia
        Volúmenes moderados y protección básica
        """
        logger.info("🔧 Configurando valores seguros iniciales...")
        
        # Volumen seguro inicial (60%)
        self._amixer('Headphone', '60%')
        self._amixer('Speaker', '60%')
        
        # Ganancia de captura moderada
        self._amixer('Capture', '70%')
        
        # Habilitar salidas de audio
        self._amixer('Left Output Mixer PCM', 'on')
        self._amixer('Right Output Mixer PCM', 'on')
        
        # Habilitar entradas de micrófono
        self._amixer('Left Input Mixer Boost', 'on')
        self._amixer('Right Input Mixer Boost', 'on')
        
        # Activar alimentación de micrófono electret
        self._amixer('Mic Bias', 'on')
        
        # Configurar modo normal por defecto
        self.set_mode_normal()
        
        logger.info("✅ WM8960 configurado con valores seguros")
    
    def set_eq_band(self, band, value_db):
        """
        Configura una banda específica del ecualizador
        
        Args:
            band: Número de banda (1-5)
            value_db: Valor en dB (-12 a +12)
        """
        control_name = f'EQ{band}'
        
        # Formatear valor para amixer
        if value_db > 0:
            value_str = f'+{int(value_db)}'
        elif value_db == 0:
            value_str = '0'
        else:
            value_str = str(int(value_db))
        
        return self._amixer(control_name, value_str)
    
    def set_volume(self, volume_percent):
        """
        Ajusta el volumen de salida
        
        Args:
            volume_percent: Volumen 0-100% (limitado a 85% para seguridad)
        """
        # Limitar volumen máximo para protección
        safe_volume = min(volume_percent, 85)
        
        self._amixer('Headphone', f'{safe_volume}%')
        self._amixer('Speaker', f'{safe_volume}%')
        
        logger.info(f"🔊 Volumen ajustado a {safe_volume}%")
    
    # ========== MODOS PRECONFIGURADOS ==========
    
    def set_mode_normal(self):
        """
        Modo Normal - Configuración balanceada para uso general
        
        Características:
        - Volumen moderado (65%)
        - EQ prácticamente plano
        - Leve reducción de agudos para comodidad
        """
        logger.info("🎧 Activando MODO NORMAL")
        self.current_mode = 'NORMAL'
        
        # Volumen moderado
        self.set_volume(65)
        
        # Ecualizador prácticamente neutro
        self.set_eq_band(1, 0)    # Bass: 0dB (neutro)
        self.set_eq_band(2, 0)    # Low-mid: 0dB (neutro)
        self.set_eq_band(3, 0)    # Mid: 0dB (neutro)
        self.set_eq_band(4, 0)    # High-mid: 0dB (neutro)
        self.set_eq_band(5, -3)   # Treble: -3dB (leve reducción)
        
        logger.info("✅ Modo NORMAL activado")
        logger.info("   Configuración: Balanceada, uso general")
    
    def set_mode_school(self):
        """
        Modo Escuela - Optimizado para escuchar voces en ambiente educativo
        
        Características:
        - Volumen reducido (60%)
        - Realce de frecuencias de voz (800Hz-2.5kHz)
        - Reducción de graves y agudos
        - Ideal para clases, conferencias, bibliotecas
        """
        logger.info("🏫 Activando MODO ESCUELA")
        self.current_mode = 'SCHOOL'
        
        # Volumen más bajo para entorno educativo
        self.set_volume(60)
        
        # Ecualizador optimizado para claridad de voz
        self.set_eq_band(1, -6)   # Bass: -6dB (reduce ruido grave)
        self.set_eq_band(2, +3)   # Low-mid: +3dB (calidez de voz)
        self.set_eq_band(3, +6)   # Mid: +6dB (claridad de voz - IMPORTANTE)
        self.set_eq_band(4, +3)   # High-mid: +3dB (consonantes claras)
        self.set_eq_band(5, -6)   # Treble: -6dB (reduce siseo y agudos molestos)
        
        logger.info("✅ Modo ESCUELA activado")
        logger.info("   Configuración: Realce de voces, reducción de ruido")
    
    def set_mode_transport(self):
        """
        Modo Transporte - Cancelación agresiva de ruido de baja frecuencia
        
        Características:
        - Volumen bajo (55%)
        - Eliminación de graves (motores, vibraciones)
        - Preservación de voces para anuncios importantes
        - Ideal para autobús, tren, avión
        """
        logger.info("🚌 Activando MODO TRANSPORTE")
        self.current_mode = 'TRANSPORT'
        
        # Volumen más bajo (el ruido ambiente ya está reducido)
        self.set_volume(55)
        
        # Ecualizador: eliminar ruido de motor y vibraciones
        self.set_eq_band(1, -12)  # Bass: -12dB (ELIMINA ruido de motor)
        self.set_eq_band(2, -6)   # Low-mid: -6dB (reduce vibraciones)
        self.set_eq_band(3, +4)   # Mid: +4dB (preserva voces/anuncios)
        self.set_eq_band(4, 0)    # High-mid: 0dB (neutro)
        self.set_eq_band(5, -9)   # Treble: -9dB (reduce ruido agudo)
        
        logger.info("✅ Modo TRANSPORTE activado")
        logger.info("   Configuración: Cancelación de ruido de motor")
    
    def get_current_mode(self):
        """Retorna el modo actual"""
        return self.current_mode
    
    def test_audio(self):
        """
        Prueba rápida de audio
        Reproduce un tono de prueba si está disponible
        """
        logger.info("🧪 Ejecutando prueba de audio...")
        try:
            subprocess.run(['speaker-test', '-c2', '-t', 'wav', '-l1'],
                         timeout=5, capture_output=True)
            logger.info("✅ Prueba de audio completada")
        except Exception as e:
            logger.error(f"❌ Error en prueba de audio: {e}")


# ========== FUNCIÓN DE PRUEBA ==========

def main():
    """
    Función principal para probar el controlador
    Permite probar cada modo manualmente
    """
    print("=" * 60)
    print("TEARIS - WM8960 Controller Test")
    print("=" * 60)
    print()
    
    try:
        # Crear controlador
        controller = WM8960Controller()
        
        print("\nControlador inicializado correctamente")
        print("\nModos disponibles:")
        print("  1. Modo Normal")
        print("  2. Modo Escuela")
        print("  3. Modo Transporte")
        print("  4. Prueba de audio")
        print("  0. Salir")
        print()
        
        while True:
            try:
                choice = input("Selecciona una opción (0-4): ").strip()
                
                if choice == "1":
                    controller.set_mode_normal()
                    print("✅ Escucha el audio - debería sonar balanceado\n")
                    
                elif choice == "2":
                    controller.set_mode_school()
                    print("✅ Escucha el audio - las voces deberían sonar más claras\n")
                    
                elif choice == "3":
                    controller.set_mode_transport()
                    print("✅ Escucha el audio - los graves deberían reducirse\n")
                    
                elif choice == "4":
                    controller.test_audio()
                    
                elif choice == "0":
                    print("\n👋 Saliendo...")
                    break
                    
                else:
                    print("❌ Opción inválida\n")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrumpido por el usuario")
                break
                
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        print("\nVerifica que:")
        print("  - El WM8960 esté correctamente instalado")
        print("  - El comando 'amixer' esté disponible")
        print("  - Tengas permisos para controlar el audio")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
