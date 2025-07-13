import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class BatteryService {
  final Guid batteryServiceUuid = Guid("0000180F-0000-1000-8000-00805f9b34fb");
  final Guid batteryLevelCharacteristicUuid = Guid("00002A19-0000-1000-8000-00805f9b34fb");

  Future<int?> readBatteryLevel(BluetoothDevice device) async {
    try {
      await device.discoverServices();
      final services = await device.services.first;

      for (var service in services) {
        if (service.serviceUuid == batteryServiceUuid) {
          for (var characteristic in service.characteristics) {
            if (characteristic.characteristicUuid == batteryLevelCharacteristicUuid) {
              final value = await characteristic.read();
              return value.isNotEmpty ? value.first : null;
            }
          }
        }
      }

      return null;
    } catch (e) {
      print("❌ Error al leer batería: $e");
      return null;
    }
  }
}
