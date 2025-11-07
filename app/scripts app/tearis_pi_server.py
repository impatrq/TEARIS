#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import logging
import subprocess

# ================================================
# CONFIGURACIÓN DE LOGS
# ================================================
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("TEARIS-BLE")

# ================================================
# UUIDs
# ================================================
SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
VOLUME_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'
MODE_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef2'
STATUS_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef3'
BATTERY_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef4'
DEVICE_INFO_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef5'

# ================================================
# CONFIGURACIÓN DE BLUEZ
# ================================================
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
ADAPTER_IFACE = 'org.bluez.Adapter1'

# ================================================
# CONTROLADOR WM8960
# ================================================
class WM8960Controller:
    def __init__(self):
        logger.info("🎵 Inicializando WM8960 Controller...")
        self.mode = "normal"
        self.volume = 65
        self.initialize_safe_defaults()

    def initialize_safe_defaults(self):
        logger.info("🔧 Configurando valores seguros iniciales...")
        try:
            subprocess.run(["amixer", "-c", "wm8960soundcard", "sset", "Mic Bias", "on"], check=True)
        except subprocess.CalledProcessError:
            logger.warning("⚠️ No se pudo configurar Mic Bias (puede no estar presente)")
        self.set_mode("normal")
        self.set_volume(self.volume)
        logger.info("✅ WM8960 configurado con valores seguros")

    def set_volume(self, volume):
        self.volume = max(0, min(100, int(volume)))
        try:
            subprocess.run(["amixer", "-c", "wm8960soundcard", "sset", "Playback Volume", f"{self.volume}%"], check=True)
            logger.info(f"🔊 Volumen ajustado a {self.volume}%")
        except subprocess.CalledProcessError:
            logger.error("❌ Error ajustando volumen (verifica que el dispositivo esté activo)")

    def set_mode(self, mode):
        self.mode = mode
        logger.info(f"🎧 Activando modo: {mode.upper()}")
        try:
            subprocess.run(["amixer", "-c", "wm8960soundcard", "sset", "EQ1", "0"], check=True)
            subprocess.run(["amixer", "-c", "wm8960soundcard", "sset", "EQ2", "0"], check=True)
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Error configurando ecualizador (puede no estar disponible)")
        logger.info(f"✅ Modo {mode.upper()} activado")

# ================================================
# CLASES BASE BLE
# ================================================
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/org/tearis/service'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(TearisService(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.ObjectManager',
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for chrc in service.get_characteristics():
                response[chrc.get_path()] = chrc.get_properties()
        return response


class Service(dbus.service.Object):
    PATH_BASE = '/org/tearis/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
            }
        }

    def get_characteristics(self):
        return self.characteristics

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)


class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s'),
            }
        }

# ================================================
# SERVICIO TEARIS PRINCIPAL
# ================================================
class TearisService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, SERVICE_UUID, True)
        self.add_characteristic(VolumeCharacteristic(bus, 0, self))
        self.add_characteristic(ModeCharacteristic(bus, 1, self))
        self.add_characteristic(StatusCharacteristic(bus, 2, self))
        self.add_characteristic(BatteryCharacteristic(bus, 3, self))
        self.add_characteristic(DeviceInfoCharacteristic(bus, 4, self))

# ================================================
# CARACTERÍSTICAS BLE
# ================================================
class VolumeCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(bus, index, VOLUME_CHARACTERISTIC_UUID, ['read', 'write', 'notify'], service)
        self.volume_level = 65

    def ReadValue(self, options):
        logger.info(f"📖 Leyendo volumen actual: {self.volume_level}%")
        return [dbus.Byte(self.volume_level)]

    def WriteValue(self, value, options):
        if not value:
            logger.warning("⚠️ Valor vacío recibido para volumen")
            return
        new_volume = int(value[0])
        logger.info(f"🔊 Ajustando volumen a: {new_volume}%")
        wm8960.set_volume(new_volume)
        self.volume_level = new_volume


class ModeCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(bus, index, MODE_CHARACTERISTIC_UUID, ['read', 'write', 'notify'], service)
        self.mode = "normal"

    def ReadValue(self, options):
        logger.info(f"📖 Leyendo modo actual: {self.mode}")
        return [dbus.Byte(ord(self.mode[0]))]

    def WriteValue(self, value, options):
        if not value:
            logger.warning("⚠️ Valor vacío recibido para modo")
            return
        new_mode = chr(value[0])
        logger.info(f"🎧 Cambiando modo a: {new_mode}")
        wm8960.set_mode(new_mode)
        self.mode = new_mode


class StatusCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(bus, index, STATUS_CHARACTERISTIC_UUID, ['read', 'notify'], service)
        self.status = True

    def ReadValue(self, options):
        logger.info(f"📖 Leyendo estado: {self.status}")
        return [dbus.Byte(1 if self.status else 0)]


class BatteryCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(bus, index, BATTERY_CHARACTERISTIC_UUID, ['read', 'notify'], service)
        self.battery_level = 99

    def ReadValue(self, options):
        logger.info(f"🔋 Nivel de batería: {self.battery_level}%")
        return [dbus.Byte(self.battery_level)]


class DeviceInfoCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(bus, index, DEVICE_INFO_CHARACTERISTIC_UUID, ['read'], service)
        self.device_name = "TEARIS"
        self.version = "1.0.0"

    def ReadValue(self, options):
        info = f"{self.device_name} v{self.version}"
        logger.info(f"📖 Info del dispositivo: {info}")
        return [dbus.Byte(b) for b in info.encode()]

# ================================================
# INICIALIZACIÓN DEL SERVIDOR BLE
# ================================================
def main():
    global wm8960
    wm8960 = WM8960Controller()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter = "/org/bluez/hci0"
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)

    app = Application(bus)

    logger.info('=' * 60)
    logger.info('✅ TEARIS BLE Server is running!')
    logger.info('📲 Dispositivo visible como: TEARIS')
    logger.info('Esperando conexiones desde la app...')
    logger.info('=' * 60)

    service_manager.RegisterApplication(app.get_path(), {},
        reply_handler=lambda: logger.info("✅ GATT app registrada correctamente"),
        error_handler=lambda e: logger.error(f"❌ Error registrando app GATT: {e}"))

    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.info("👋 Apagando servidor TEARIS...")

if __name__ == '__main__':
    main()
