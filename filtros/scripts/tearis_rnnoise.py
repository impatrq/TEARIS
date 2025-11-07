#!/usr/bin/env python3
"""
TEARIS - Supresión de ruido en tiempo real con RNNoise
Latencia ultra-baja (~10-20ms) optimizado para Raspberry Pi
"""

import numpy as np
import sounddevice as sd
import subprocess
import os
import queue
import threading
import logging
from ctypes import CDLL, c_void_p, c_int, POINTER, c_float

# Configuración
SAMPLE_RATE = 48000
CHANNELS = 2
FRAME_SIZE = 480  # RNNoise usa frames de 10ms (480 samples @ 48kHz)
DEVICE_INPUT = 0
DEVICE_OUTPUT = 0

audio_queue = queue.Queue(maxsize=5)
processed_queue = queue.Queue(maxsize=5)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class RNNoiseProcessor:
    """
    Wrapper de RNNoise para procesamiento en tiempo real
    Usa la librería compilada de RNNoise
    """
    
    def __init__(self, lib_path=None):
        # Buscar librería RNNoise
        if lib_path is None:
            lib_path = self._find_rnnoise_lib()
        
        if not lib_path:
            raise RuntimeError(
                "No se encontró librería RNNoise. "
                "Compila RNNoise primero con: cd ~/rnnoise && make"
            )
        
        logger.info(f"📚 Cargando RNNoise desde: {lib_path}")
        
        # Cargar librería
        self.lib = CDLL(lib_path)
        
        # Definir funciones de la API
        self.lib.rnnoise_create.restype = c_void_p
        self.lib.rnnoise_create.argtypes = [c_void_p]
        
        self.lib.rnnoise_destroy.argtypes = [c_void_p]
        
        self.lib.rnnoise_process_frame.restype = c_float
        self.lib.rnnoise_process_frame.argtypes = [
            c_void_p,  # state
            POINTER(c_float),  # out
            POINTER(c_float)   # in
        ]
        
        # Crear estados RNNoise (uno por canal)
        self.states = [self.lib.rnnoise_create(None) for _ in range(CHANNELS)]
        
        logger.info(f"✓ RNNoise inicializado con {CHANNELS} canales")
        logger.info(f"  Frame size: {FRAME_SIZE} samples (10ms)")
        
    def _find_rnnoise_lib(self):
        """Busca la librería RNNoise compilada"""
        possible_paths = [
            os.path.expanduser("~/rnnoise/.libs/librnnoise.so"),
            os.path.expanduser("~/rnnoise/.libs/librnnoise.so.0"),
            "/usr/local/lib/librnnoise.so",
            "/usr/lib/librnnoise.so",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def process_frame(self, audio_frame):
        """
        Procesa un frame de audio con RNNoise
        audio_frame: numpy array de shape (480, 2) float32
        """
        try:
            # RNNoise espera float32 [-32768, 32767] (PCM16 range)
            audio_scaled = audio_frame * 32768.0
            
            # Asegurar que sea 2D
            if audio_scaled.ndim == 1:
                audio_scaled = audio_scaled.reshape(-1, 1)
            
            # Si solo hay 1 canal, duplicarlo para estéreo
            if audio_scaled.shape[1] == 1:
                audio_scaled = np.hstack([audio_scaled, audio_scaled])
            
            # Procesar cada canal independientemente
            output = np.zeros_like(audio_scaled)
            
            for ch in range(min(CHANNELS, audio_scaled.shape[1])):
                # Extraer canal
                channel_data = audio_scaled[:, ch].astype(np.float32)
                
                # Asegurar tamaño correcto
                if len(channel_data) != FRAME_SIZE:
                    if len(channel_data) < FRAME_SIZE:
                        channel_data = np.pad(channel_data, (0, FRAME_SIZE - len(channel_data)))
                    else:
                        channel_data = channel_data[:FRAME_SIZE]
                
                # Crear buffer de salida
                output_buffer = np.zeros(FRAME_SIZE, dtype=np.float32)
                
                # Llamar a RNNoise
                vad_prob = self.lib.rnnoise_process_frame(
                    self.states[ch],
                    output_buffer.ctypes.data_as(POINTER(c_float)),
                    channel_data.ctypes.data_as(POINTER(c_float))
                )
                
                # Guardar resultado
                output[:len(output_buffer), ch] = output_buffer
            
            # Volver a rango [-1, 1]
            output = output / 32768.0
            
            # Asegurar forma correcta de salida
            if output.shape != audio_frame.shape:
                if audio_frame.ndim == 1:
                    output = output.flatten()
                elif audio_frame.shape[1] != output.shape[1]:
                    output = output[:, :audio_frame.shape[1]]
            
            return output.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error procesando frame: {e}", exc_info=True)
            return audio_frame
    
    def __del__(self):
        """Limpiar recursos"""
        if hasattr(self, 'states'):
            for state in self.states:
                self.lib.rnnoise_destroy(state)


def audio_callback(indata, outdata, frames, time_info, status):
    """Callback de audio para tiempo real"""
    if status:
        logger.warning(f"Status: {status}")
    
    try:
        audio_queue.put_nowait(indata.copy())
        processed = processed_queue.get_nowait()
        outdata[:] = processed
    except queue.Full:
        outdata[:] = indata
    except queue.Empty:
        outdata[:] = indata


def processing_thread(processor):
    """Thread de procesamiento RNNoise"""
    logger.info("🔄 Thread de procesamiento iniciado")
    
    import time
    frame_count = 0
    total_time = 0
    last_report = time.time()
    
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=1.0)
            
            start = time.time()
            processed = processor.process_frame(audio_chunk)
            process_time = (time.time() - start) * 1000
            
            processed_queue.put_nowait(processed)
            
            frame_count += 1
            total_time += process_time
            
            # Reportar cada 10 segundos
            if time.time() - last_report > 10.0:
                avg_time = total_time / frame_count
                cpu_usage = (avg_time / 10.0) * 100  # % de CPU usado
                
                logger.info(
                    f"⚡ Latencia: {avg_time:.2f}ms | "
                    f"CPU: ~{cpu_usage:.1f}% | "
                    f"Queue: {audio_queue.qsize()}/{processed_queue.qsize()}"
                )
                
                frame_count = 0
                total_time = 0
                last_report = time.time()
            
        except queue.Empty:
            continue
        except queue.Full:
            logger.warning("Cola llena")
        except Exception as e:
            logger.error(f"Error: {e}")


def main():
    """Función principal"""
    logger.info("=" * 70)
    logger.info("🎧 TEARIS - RNNoise en Tiempo Real")
    logger.info("Supresión de ruido de ultra-baja latencia")
    logger.info("=" * 70)
    
    # Verificar que RNNoise está compilado
    rnnoise_lib = None
    possible_paths = [
        os.path.expanduser("~/rnnoise/.libs/librnnoise.so"),
        os.path.expanduser("~/rnnoise/.libs/librnnoise.so.0"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            rnnoise_lib = path
            break
    
    if not rnnoise_lib:
        logger.error("❌ RNNoise no encontrado")
        logger.info("\nPara instalar RNNoise:")
        logger.info("  cd ~")
        logger.info("  git clone https://github.com/xiph/rnnoise.git")
        logger.info("  cd rnnoise")
        logger.info("  ./autogen.sh")
        logger.info("  ./configure")
        logger.info("  make")
        return
    
    # Inicializar procesador
    logger.info("\n🔧 Inicializando RNNoise...")
    processor = RNNoiseProcessor(rnnoise_lib)
    
    # Iniciar thread
    logger.info("🚀 Iniciando procesamiento...")
    proc_thread = threading.Thread(
        target=processing_thread,
        args=(processor,),
        daemon=True
    )
    proc_thread.start()
    
    # Pre-llenar buffers
    logger.info("📦 Preparando buffers...")
    for _ in range(3):
        processed_queue.put(np.zeros((FRAME_SIZE, CHANNELS), dtype=np.float32))
    
    logger.info(f"\n⚙️  Configuración:")
    logger.info(f"  Sample Rate: {SAMPLE_RATE} Hz")
    logger.info(f"  Frame Size: {FRAME_SIZE} samples (10ms)")
    logger.info(f"  Canales: {CHANNELS}")
    logger.info(f"  Latencia esperada: ~15-20ms")
    logger.info(f"  CPU esperado: ~10-15% (RPi Zero 2W)")
    
    try:
        with sd.Stream(
            device=(DEVICE_INPUT, DEVICE_OUTPUT),
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SIZE,
            channels=CHANNELS,
            dtype=np.float32,
            callback=audio_callback,
            latency='low'
        ):
            logger.info("\n" + "=" * 70)
            logger.info("✅ Sistema RNNoise activo")
            logger.info("🔇 Supresión de ruido en tiempo real")
            logger.info("⚡ Latencia ultra-baja optimizada para RPi")
            logger.info("=" * 70)
            logger.info("\n💡 Prueba con ruido de fondo, ventilador, etc.")
            logger.info("Presiona Ctrl+C para detener\n")
            
            while True:
                sd.sleep(1000)
                
    except KeyboardInterrupt:
        logger.info("\n⏹️  Deteniendo sistema...")
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
    finally:
        logger.info("👋 Sistema detenido")


if __name__ == "__main__":
    main()
