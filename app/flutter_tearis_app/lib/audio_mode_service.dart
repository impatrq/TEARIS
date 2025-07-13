import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class AudioModeService {
  final Guid serviceUuid = Guid("12345678-1234-5678-1234-56789abcdef0");
  final Guid characteristicUuid = Guid("abcdef12-3456-7890-abcd-ef1234567890");

  Future<void> activateAmbientMode(BluetoothDevice device) async {
    try {
      await device.discoverServices();
      var services = await device.services.first;

      for (var service in services) {
        if (service.serviceUuid == serviceUuid) {
          for (var characteristic in service.characteristics) {
            if (characteristic.characteristicUuid == characteristicUuid) {
              await characteristic.write([0x02]);
              print("✅ Modo ambiente activado");
              return;
            }
          }
        }
      }

      print("❌ Característica no encontrada.");
    } catch (e) {
      print("❌ Error al activar modo ambiente: $e");
    }
  }
}
