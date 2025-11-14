#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEARIS BLE Server - Versión Final y Robusta
"""

import os
import sys
import signal
import subprocess
import logging
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
from ctypes import c_ubyte
import numpy as np
import sounddevice as sd
import queue
import threading
from ctypes import CDLL, c_void_p, POINTER, c_float
import time

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("TEARIS-BLE")

# Constants / UUIDs
SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
BATTERY_UUID = '12345678-1234-5678-1234-56789abcdef1'
MODE_UUID = '12345678-1234-5678-1234-56789abcdef2'
STATUS_UUID = '12345678-1234-5678-1234-56789abcdef3'
VOLUME_UUID = '12345678-1234-5678-1234-56789abcdef4'
AUDIO_STREAM_UUID = '12345678-1234-5678-1234-56789abcdef5'

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'

# Nombre del dispositivo que verá la app
ADAPTER_NAME = 'TEARIS-Audio'

# RNNoise config
SAMPLE_RATE = 48000
CHANNELS = 2
FRAME_SIZE = 480

# Variables de entorno para dispositivos de audio (configurado a hw:1,0)
DEVICE_INPUT = os.environ.get('TEARIS_AUDIO_INPUT', 'hw:1,0')
DEVICE_OUTPUT = os.environ.get('TEARIS_AUDIO_OUTPUT', 'hw:1,0')

# Globals
wm8960 = None
mainloop = None
audio_queue = queue.Queue(maxsize=5)

# ========================================
# Clase para Anuncio BLE
# ========================================
class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = [SERVICE_UUID]
        # Hemos quitado 'local_name' y 'include_tx_power' para probar
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = {
            'Type': self.ad_type,
            'ServiceUUIDs': self.service_uuids
            # Solo las propiedades más básicas
        }
        return {LE_ADVERTISING_MANAGER_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISING_MANAGER_IFACE:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownInterface: Interface not found')
        return self.get_properties()[LE_ADVERTISING_MANAGER_IFACE]
# ========================================
# RNNoise Processor Class
# ========================================
class RNNoiseProcessor:
    def __init__(self, lib_path=None):
        if lib_path is None:
            lib_path = self._find_rnnoise_lib()
        
        if not lib_path:
            raise RuntimeError("No se encontró librería RNNoise")
        
        logger.info(f"🔊 Cargando RNNoise desde: {lib_path}")
        self.lib = CDLL(lib_path)
        
        self.lib.rnnoise_create.restype = c_void_p
        self.lib.rnnoise_create.argtypes = [c_void_p]
        self.lib.rnnoise_destroy.argtypes = [c_void_p]
        
        self.lib.rnnoise_process_frame.restype = c_float
        self.lib.rnnoise_process_frame.argtypes = [
            c_void_p,
            POINTER(c_float),  # output
            POINTER(c_float)   # input
        ]
        
        self.states = [self.lib.rnnoise_create(None) for _ in range(CHANNELS)]
        logger.info(f"✅ RNNoise inicializado con {CHANNELS} canales")
    
    def _find_rnnoise_lib(self):
        possible_paths = [
            "/home/tearis/rnnoise/.libs/librnnoise.so",
            "/home/tearis/rnnoise/.libs/librnnoise.so.0",
            "/home/tearis/rnnoise/.libs/librnnoise.so.0.4.1",
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
        try:
            audio_scaled = audio_frame * 32768.0
            if audio_scaled.ndim == 1:
                audio_scaled = audio_scaled.reshape(-1, 1)
            if audio_scaled.shape[1] == 1:
                audio_scaled = np.hstack([audio_scaled, audio_scaled])
            if audio_scaled.shape[0] != FRAME_SIZE:
                logger.warning(f"⚠️ Frame size mismatch: {audio_scaled.shape[0]} != {FRAME_SIZE}")
                if audio_scaled.shape[0] < FRAME_SIZE:
                    audio_scaled = np.pad(audio_scaled, ((0, FRAME_SIZE - audio_scaled.shape[0]), (0, 0)))
                else:
                    audio_scaled = audio_scaled[:FRAME_SIZE, :]
            output = np.zeros_like(audio_scaled)
            for ch in range(min(CHANNELS, audio_scaled.shape[1])):
                channel_data = audio_scaled[:, ch].astype(np.float32)
                output_buffer = np.zeros(FRAME_SIZE, dtype=np.float32)
                self.lib.rnnoise_process_frame(self.states[ch], output_buffer.ctypes.data_as(POINTER(c_float)), channel_data.ctypes.data_as(POINTER(c_float)))
                output[:, ch] = output_buffer
            output = output / 32768.0
            return output
        except Exception as e:
            logger.error(f"❌ Error procesando frame: {e}")
            return audio_frame
    
    def __del__(self):
        if hasattr(self, 'states'):
            for state in self.states:
                self.lib.rnnoise_destroy(state)

# ========================================
# WM8960 Controller
# ========================================
class WM8960Controller:
    def __init__(self):
        logger.info("🎛️ Inicializando WM8960 Controller...")
        self.mode = "normal"
        self.volume = 65
        self.rnnoise_processor = None
        self.audio_stream = None
        self.rnnoise_enabled = False
        self.initialize_safe_defaults()
        self.start_audio_stream()
    
    def initialize_safe_defaults(self):
        logger.info("🔧 Configurando valores seguros iniciales...")
        try_cmd = lambda args: subprocess.run(args, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try_cmd(["amixer", "-c", "1", "sset", "Headphone", f"{self.volume}%"])
        try_cmd(["amixer", "-c", "1", "sset", "Capture", "70%"])
        try_cmd(["amixer", "-c", "1", "sset", "Left Output Mixer PCM", "on"])
        try_cmd(["amixer", "-c", "1", "sset", "Right Output Mixer PCM", "on"])
        logger.info("✅ WM8960: valores seguros aplicados")
    
    def set_volume(self, vol):
        vol = max(0, min(85, int(vol)))
        self.volume = vol
        try:
            subprocess.run(["amixer", "-c", "1", "sset", "Headphone", f"{self.volume}%"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"🔊 Volumen ajustado a {self.volume}%")
        except Exception as e:
            logger.error(f"❌ Error ajustando volumen: {e}")
    
    def set_eq_flat(self):
        for i in range(1, 6):
            subprocess.run(["amixer", "-c", "1", "sset", f"EQ{i}", "0"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("🎚️ EQ: plana aplicada")
    
    def set_eq_school(self):
        eq_settings = [("EQ1", "+0"), ("EQ2", "+3"), ("EQ3", "+6"), ("EQ4", "+3"), ("EQ5", "+0")]
        for control, value in eq_settings:
            subprocess.run(["amixer", "-c", "1", "sset", control, value], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("🎚️ EQ: modo ESCUELA aplicado")

    def start_audio_stream(self):
        if self.audio_stream and self.audio_stream.active:
            return
        logger.info(f"🎤 Iniciando stream de audio base...")
        
        def main_audio_callback(indata, outdata, frames, time_info, status):
            if status:
                logger.warning(f"⚠️ Audio status: {status}")
            try:
                if self.rnnoise_enabled and self.rnnoise_processor:
                    num_frames = indata.shape[0]
                    if num_frames == FRAME_SIZE:
                        processed = self.rnnoise_processor.process_frame(indata)
                        outdata[:] = processed
                    else:
                        for i in range(0, num_frames, FRAME_SIZE):
                            chunk = indata[i:i+FRAME_SIZE]
                            if chunk.shape[0] == FRAME_SIZE:
                                processed_chunk = self.rnnoise_processor.process_frame(chunk)
                                outdata[i:i+FRAME_SIZE] = processed_chunk
                            else:
                                outdata[i:] = chunk
                else:
                    outdata[:] = indata
                try:
                    audio_queue.put_nowait(outdata.copy())
                except queue.Full:
                    pass
            except Exception as e:
                logger.error(f"❌ Error en callback: {e}")
                outdata[:] = indata
        
        try:
            self.audio_stream = sd.Stream(device=(DEVICE_INPUT, DEVICE_OUTPUT), samplerate=SAMPLE_RATE, blocksize=960, channels=CHANNELS, dtype=np.float32, callback=main_audio_callback, latency=0.25)
            self.audio_stream.start()
            logger.info("✅ Stream de audio base activo")
            def metrics_thread():
                while self.audio_stream.active:
                    time.sleep(5)
                    logger.info(f"⚙️ Buffer BLE: {audio_queue.qsize()} | RNNoise: {'ON' if self.rnnoise_enabled else 'OFF'} | Stream: OK")
            threading.Thread(target=metrics_thread, daemon=True).start()
        except Exception as e:
            logger.error(f"❌ Error creando Stream de audio: {e}")

    def start_rnnoise(self):
        if self.rnnoise_processor:
            logger.info("ℹ️ RNNoise ya está inicializado.")
            self.rnnoise_enabled = True
            return
        logger.info("🎤 Inicializando procesador RNNoise...")
        try:
            self.rnnoise_processor = RNNoiseProcessor()
            self.rnnoise_enabled = True
            logger.info("✅ RNNoise activado.")
        except RuntimeError as e:
            logger.error(f"❌ {e}")
            logger.error("Compila RNNoise primero: cd ~/rnnoise && ./autogen.sh && ./configure && make")
            self.rnnoise_enabled = False
    
    def stop_rnnoise(self):
        if not self.rnnoise_enabled and not self.rnnoise_processor:
            return
        logger.info("🛑 Desactivando RNNoise...")
        self.rnnoise_enabled = False
        if self.rnnoise_processor:
            del self.rnnoise_processor
            self.rnnoise_processor = None
            logger.info("✅ Procesador RNNoise limpiado")

    def set_mode(self, mode):
        self.mode = mode.lower()
    
        if not self.audio_stream or not self.audio_stream.active:
            self.start_audio_stream()
    
    # Ahora acepta tanto "escuela" como "mode_school"
        if self.mode == "escuela" or self.mode == "mode_school":
            logger.info("🎓 MODO 'ESCUELA' RECIBIDO. LLAMANDO A start_rnnoise().")
            self.set_eq_school()
            self.start_rnnoise()
        else:
            logger.info("🔧 MODO 'NORMAL/OTRO' RECIBIDO. ASEGURANDO RNNoise DESACTIVADO.")
            self.set_eq_flat()
            self.stop_rnnoise()
    
        logger.info(f"✅ Modo {mode.upper()} activado (RNNoise: {'ON' if self.rnnoise_enabled else 'OFF'})")


    def cleanup(self):
        logger.info("🛑 Limpiando WM8960...")
        self.stop_rnnoise()
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
            logger.info("✅ Stream de audio cerrado")

# ========================================
# GATT Classes - Totalmente Formateadas
# ========================================
# ========================================
# GATT Classes - Versión Robusta y Formateada
# ========================================
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(TearisService(bus, 0))
    
    def get_path(self):
        return dbus.ObjectPath(self.path)
    
    def add_service(self, service):
        self.services.append(service)
    
    @dbus.service.method(DBUS_OM_IFACE)
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return dbus.Dictionary(response, signature='oa{sa{sv}}')

class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'
    
    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)
    
    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: dbus.Dictionary({
                'UUID': dbus.String(self.uuid),
                'Primary': dbus.Boolean(self.primary),
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }, signature='sv')
        }
    
    def get_path(self):
        return dbus.ObjectPath(self.path)
    
    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)
    
    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result
    
    def get_characteristics(self):
        return self.characteristics
    
    @dbus.service.method(DBUS_PROP_IFACE,
                        in_signature='s',
                        out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                'org.freedesktop.DBus.Error.UnknownInterface: '
                'Interface not found')
        return self.get_properties()[GATT_SERVICE_IFACE]

class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = dbus.Array(flags, signature='s')
        self.value = dbus.Array([], signature='y')
        dbus.service.Object.__init__(self, bus, self.path)
    
    def get_properties(self):
        return {
            GATT_CHRC_IFACE: dbus.Dictionary({
                'Service': dbus.ObjectPath(self.service.get_path()),
                'UUID': dbus.String(self.uuid),
                'Flags': self.flags,
                'Value': self.value
            }, signature='sv')
        }
    
    def get_path(self):
        return dbus.ObjectPath(self.path)
    
    @dbus.service.method(DBUS_PROP_IFACE,
                        in_signature='s',
                        out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                'org.freedesktop.DBus.Error.UnknownInterface: '
                'Interface not found')
        return self.get_properties()[GATT_CHRC_IFACE]
    
    @dbus.service.signal(DBUS_PROP_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class TearisService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, SERVICE_UUID, True)
        self.add_characteristic(BatteryCharacteristic(bus, 0, self))
        self.add_characteristic(ModeCharacteristic(bus, 1, self))
        self.add_characteristic(StatusCharacteristic(bus, 2, self))
        self.add_characteristic(VolumeCharacteristic(bus, 3, self))
        self.add_characteristic(AudioStreamCharacteristic(bus, 4, self))

class BatteryCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, BATTERY_UUID, ['read', 'notify'], service)
        self.value = dbus.Array([dbus.Byte(100)], signature='y')
        self.notifying = False
    
    def ReadValue(self, options):
        logger.info("🔋 Leyendo batería")
        return self.value
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        logger.info("🔔 Iniciando notificaciones de batería...")
        GLib.timeout_add(10000, self.update_battery)
    
    def StopNotify(self):
        self.notifying = False
        logger.info("🔕 Notificaciones de batería detenidas.")
    
    def update_battery(self):
        if not self.notifying:
            return False
        self.value = dbus.Array([dbus.Byte(self.value[0] - 1 if self.value[0] > 0 else 0)], signature='y')
        logger.info(f"🔋 Battery updated: {self.value[0]}%")
        self.PropertiesChanged(GATT_CHRC_IFACE, dbus.Dictionary({'Value': self.value}, signature='sv'), [])
        return True

class ModeCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, MODE_UUID, ['read', 'write'], service)
        self.value = dbus.Array([dbus.Byte(ord(c)) for c in "NORMAL"], signature='y')
    
    def ReadValue(self, options):
        logger.info("📖 Leyendo modo")
        return self.value
    
    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        self.value = value
        mode_str = ''.join([chr(b) for b in value])
        logger.info(f"✏️ Modo escrito: {mode_str}")
        wm8960.set_mode(mode_str)
class StatusCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, STATUS_UUID, ['read'], service)
        self.value = dbus.Array([dbus.Byte(ord(c)) for c in "OK"], signature='y')
    
    def ReadValue(self, options):
        logger.info("📊 Leyendo status")
        return self.value

class VolumeCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, VOLUME_UUID, ['read', 'write'], service)
        self.value = dbus.Array([dbus.Byte(65)], signature='y')
    
    def ReadValue(self, options):
        logger.info("🔊 Leyendo volumen")
        return self.value
    
    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        self.value = value
        vol = value[0]
        logger.info(f"✏️ Volumen escrito: {vol}%")
        wm8960.set_volume(vol)
class AudioStreamCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, AUDIO_STREAM_UUID, ['notify'], service)
        self.notifying = False
        self.audio_read_source = None
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        logger.info("🎵 Iniciando streaming de audio...")
        self.audio_read_source = GLib.timeout_add(10, self._notify_from_queue)
    
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
        logger.info("🛑 Audio streaming detenido.")
        if self.audio_read_source:
            GLib.source_remove(self.audio_read_source)
            self.audio_read_source = None
    
    def _notify_from_queue(self):
        if not self.notifying:
            return False
        
        try:
            processed = audio_queue.get_nowait()
            data = (processed * 32767).astype(np.int16).tobytes()
            value = dbus.Array([dbus.Byte(b) for b in data], signature='y')
            self.PropertiesChanged(GATT_CHRC_IFACE, dbus.Dictionary({'Value': value}, signature='sv'), [])
        except queue.Empty:
            pass
        
        return True
# ========================================
# Helper functions
# ========================================
def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for path, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return path
    return None

def register_app_cb():
    logger.info("✅ GATT application registered")

def register_app_error_cb(error):
    logger.error("❌ Failed to register application: %s", error)
    mainloop.quit()

def register_ad_cb():
    logger.info("✅ Advertisement registered")

def register_ad_error_cb(error):
    logger.error(f"❌ Failed to register advertisement: {error}")
    mainloop.quit()

# ========================================
# Cleanup y Main
# ========================================
def cleanup_and_exit(signum=None, frame=None):
    global mainloop
    logger.info("🛑 Limpiando...")
    try:
        if wm8960:
            wm8960.cleanup()
    except Exception as e:
        logger.warning(f"⚠️ Error during cleanup: {e}")
    
    if mainloop:
        mainloop.quit()

def main():
    global wm8960, mainloop
    
    logger.info("=" * 70)
    logger.info("🎧 TEARIS BLE Server - FINAL VERSION")
    logger.info("=" * 70)
    
    wm8960 = WM8960Controller()
    
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    
    adapter_path = find_adapter(bus)
    if not adapter_path:
        logger.error("❌ GattManager1 not found")
        cleanup_and_exit()
        return
    
    logger.info(f"Using adapter: {adapter_path}")
    
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path), GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path), LE_ADVERTISING_MANAGER_IFACE)
    
    advertisement = Advertisement(bus, 0, 'peripheral')
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {}, reply_handler=register_ad_cb, error_handler=register_ad_error_cb)
    
    app = Application(bus)
    service_manager.RegisterApplication(app.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
    
    wm8960.set_mode("normal")
    
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    
    mainloop = GLib.MainLoop()
    try:
        logger.info("✅ Server running - waiting for connections...")
        mainloop.run()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
    finally:
        logger.info("Shutting down")
        cleanup_and_exit()

if __name__ == '__main__':
    main()

