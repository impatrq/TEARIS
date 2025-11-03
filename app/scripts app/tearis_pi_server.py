#!/usr/bin/env python3
"""
TEARIS - Servidor BLE para Raspberry Pi Zero 2 W
Este script convierte la Raspberry Pi en un servidor BLE que se comunica con la app Flutter
Versión con integración WM8960 Audio HAT
"""

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import sys
import logging
import threading
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar cargar control del WM8960
try:
    from wm8960_control import WM8960Controller
    wm8960 = WM8960Controller()
    WM8960_AVAILABLE = True
    logger.info("✅ WM8960 controller cargado correctamente")
except Exception as e:
    WM8960_AVAILABLE = False
    wm8960 = None
    logger.warning(f"⚠️ WM8960 no disponible: {e}")
    logger.warning("El servidor funcionará solo con BLE (sin control de audio)")

# Constantes BLE
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

# UUIDs del servicio TEARIS (deben coincidir con la app Flutter)
TEARIS_SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
BATTERY_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'
MODE_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef2'
STATUS_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef3'
VOLUME_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef4'

class Application(dbus.service.Object):
    """
    Aplicación GATT que gestiona los servicios BLE
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(TearisService(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()
        return response


class Service(dbus.service.Object):
    """
    Clase base para servicios GATT
    """
    PATH_BASE = '/org/bluez/tearis/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
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
                'org.bluez.Error.InvalidArguments',
                'Invalid interface: ' + interface)
        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    Clase base para características GATT
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(
                    self.get_descriptor_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                'org.bluez.Error.InvalidArguments',
                'Invalid interface: ' + interface)
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        logger.info('Default ReadValue called, returning error')
        raise dbus.exceptions.DBusException(
            'org.bluez.Error.NotSupported',
            'Read not supported')

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        logger.info('Default WriteValue called, returning error')
        raise dbus.exceptions.DBusException(
            'org.bluez.Error.NotSupported',
            'Write not supported')

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        logger.info('Default StartNotify called, returning error')
        raise dbus.exceptions.DBusException(
            'org.bluez.Error.NotSupported',
            'Notify not supported')

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        logger.info('Default StopNotify called, returning error')
        raise dbus.exceptions.DBusException(
            'org.bluez.Error.NotSupported',
            'Notify not supported')


class TearisService(Service):
    """
    Servicio principal de TEARIS
    """
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, TEARIS_SERVICE_UUID, True)
        self.add_characteristic(BatteryCharacteristic(bus, 0, self))
        self.add_characteristic(ModeCharacteristic(bus, 1, self))
        self.add_characteristic(StatusCharacteristic(bus, 2, self))
        self.add_characteristic(VolumeCharacteristic(bus, 3, self))


class BatteryCharacteristic(Characteristic):
    """
    Característica para el nivel de batería
    """
    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            BATTERY_CHARACTERISTIC_UUID,
            ['read', 'notify'],
            service)
        self.notifying = False
        self.battery_level = 100  # Nivel inicial de batería
        GLib.timeout_add_seconds(10, self.update_battery)

    def ReadValue(self, options):
        logger.info(f'Battery level read: {self.battery_level}%')
        return dbus.Array([dbus.Byte(self.battery_level)])

    def StartNotify(self):
        if self.notifying:
            logger.info('Already notifying')
            return
        self.notifying = True
        logger.info('Battery notifications enabled')

    def StopNotify(self):
        if not self.notifying:
            logger.info('Not notifying')
            return
        self.notifying = False
        logger.info('Battery notifications disabled')

    def update_battery(self):
        """
        Simula la lectura del nivel de batería
        En un proyecto real, aquí leerías el nivel real de la batería
        """
        # Aquí puedes agregar código para leer la batería real
        # Por ejemplo, leyendo /sys/class/power_supply/battery/capacity
        try:
            with open('/sys/class/power_supply/BAT0/capacity', 'r') as f:
                self.battery_level = int(f.read().strip())
        except:
            # Simulación si no hay batería real
            import random
            self.battery_level = max(20, self.battery_level - random.randint(0, 2))
        
        logger.info(f'Battery updated: {self.battery_level}%')
        
        if self.notifying:
            value = dbus.Array([dbus.Byte(self.battery_level)])
            self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
        
        return True  # Continuar el timer

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class ModeCharacteristic(Characteristic):
    """
    Característica para cambiar modos de funcionamiento
    """
    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            MODE_CHARACTERISTIC_UUID,
            ['write'],
            service)
        self.current_mode = "NORMAL"

    def WriteValue(self, value, options):
        val = bytes(value).decode('utf-8')
        logger.info(f'Mode change received: {val}')
        
        if val == "MODE_SCHOOL":
            self.current_mode = "SCHOOL"
            self.activate_school_mode()
        elif val == "MODE_TRANSPORT":
            self.current_mode = "TRANSPORT"
            self.activate_transport_mode()
        elif val == "MODE_NORMAL":
            self.current_mode = "NORMAL"
            self.activate_normal_mode()
        else:
            logger.warning(f'Unknown mode: {val}')

    def activate_school_mode(self):
        """
        Activa el modo escuela - ajustes específicos para ambiente escolar
        """
        logger.info('🏫 Activating SCHOOL mode')
        
        if WM8960_AVAILABLE:
            try:
                wm8960.set_mode_school()
                logger.info('✅ WM8960 configurado para modo ESCUELA')
            except Exception as e:
                logger.error(f'❌ Error configurando WM8960: {e}')
        else:
            logger.info('ℹ️  Modo ESCUELA activado (solo BLE, sin control de audio)')

    def activate_transport_mode(self):
        """
        Activa el modo transporte - ajustes para viajes
        """
        logger.info('🚌 Activating TRANSPORT mode')
        
        if WM8960_AVAILABLE:
            try:
                wm8960.set_mode_transport()
                logger.info('✅ WM8960 configurado para modo TRANSPORTE')
            except Exception as e:
                logger.error(f'❌ Error configurando WM8960: {e}')
        else:
            logger.info('ℹ️  Modo TRANSPORTE activado (solo BLE, sin control de audio)')

    def activate_normal_mode(self):
        """
        Activa el modo normal - configuración estándar
        """
        logger.info('🎧 Activating NORMAL mode')
        
        if WM8960_AVAILABLE:
            try:
                wm8960.set_mode_normal()
                logger.info('✅ WM8960 configurado para modo NORMAL')
            except Exception as e:
                logger.error(f'❌ Error configurando WM8960: {e}')
        else:
            logger.info('ℹ️  Modo NORMAL activado (solo BLE, sin control de audio)')

class VolumeCharacteristic(Characteristic):
    """
    Característica para controlar el volumen
    """
    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            VOLUME_CHARACTERISTIC_UUID,
            ['read', 'write'],
            service)
        self.volume_level = 60  # Volumen inicial
    
    def ReadValue(self, options):
        logger.info(f'Volume read: {self.volume_level}%')
        return dbus.Array([dbus.Byte(self.volume_level)])
    
    def WriteValue(self, value, options):
        new_volume = int(value[0])
        
        # Limitar entre 0-85% (protección para hiperacusia)
        new_volume = max(0, min(85, new_volume))
        
        self.volume_level = new_volume
        logger.info(f'🔊 Volume change: {new_volume}%')
        
        if WM8960_AVAILABLE:
            try:
                wm8960.set_volume(new_volume)
                logger.info(f'✅ Volumen WM8960 ajustado a {new_volume}%')
            except Exception as e:
                logger.error(f'❌ Error ajustando volumen: {e}')
                
                
class StatusCharacteristic(Characteristic):
    """
    Característica para leer el estado general del dispositivo
    """
    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            STATUS_CHARACTERISTIC_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        if WM8960_AVAILABLE:
            status_info = "TEARIS_READY_WITH_AUDIO"
        else:
            status_info = "TEARIS_READY_BLE_ONLY"
        
        logger.info(f'Status read: {status_info}')
        return dbus.Array([dbus.Byte(c) for c in status_info.encode()])


def register_app_cb():
    logger.info('GATT application registered successfully')


def register_app_error_cb(error):
    logger.error(f'Failed to register application: {error}')
    mainloop.quit()


def find_adapter(bus):
    """
    Encuentra el adaptador Bluetooth
    """
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def main():
    global mainloop

    logger.info("=" * 60)
    logger.info("TEARIS BLE Server - Iniciando...")
    logger.info("=" * 60)
    
    if WM8960_AVAILABLE:
        logger.info("🎵 Modo: BLE + Control de Audio WM8960")
    else:
        logger.info("📡 Modo: Solo BLE (sin control de audio)")
    
    logger.info("=" * 60)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        logger.error('❌ GattManager1 interface not found')
        logger.error('Verifica que el servicio Bluetooth esté corriendo:')
        logger.error('  sudo systemctl status bluetooth')
        return

    logger.info(f'Using adapter: {adapter}')

    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        GATT_MANAGER_IFACE)

    app = Application(bus)

    logger.info('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    logger.info('=' * 60)
    logger.info('✅ TEARIS BLE Server is running!')
    logger.info('Dispositivo visible como: TEARIS')
    logger.info('Esperando conexiones desde la app...')
    logger.info('Press Ctrl+C to exit')
    logger.info('=' * 60)

    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.info('\n' + '=' * 60)
        logger.info('👋 Shutting down TEARIS BLE Server...')
        logger.info('=' * 60)


if __name__ == '__main__':
    main()
