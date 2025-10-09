import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';
import 'dart:convert';

void main() {
  runApp(const TearisApp());
}

class TearisApp extends StatelessWidget {
  const TearisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tearis',
      theme: ThemeData(
        brightness: Brightness.light,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigoAccent),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.indigo,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      debugShowCheckedModeBanner: false,
      home: const TearisHome(),
    );
  }
}

class TearisHome extends StatefulWidget {
  const TearisHome({super.key});

  @override
  State<TearisHome> createState() => _TearisHomeState();
}

class _TearisHomeState extends State<TearisHome> {
  BluetoothDevice? connectedDevice;
  BluetoothCharacteristic? batteryCharacteristic;
  BluetoothCharacteristic? modeCharacteristic;
  BluetoothCharacteristic? statusCharacteristic;
  
  String connectionStatus = "Desconectado";
  int batteryLevel = 0;
  String currentMode = "Normal";
  bool isScanning = false;
  bool isConnecting = false;
  
  List<ScanResult> scanResults = [];
  StreamSubscription? scanSubscription;
  StreamSubscription? connectionSubscription;
  StreamSubscription? batterySubscription;

  // UUIDs para el servicio BLE de TEARIS
  static const String tearisServiceUuid = "12345678-1234-5678-1234-56789abcdef0";
  static const String batteryCharUuid = "12345678-1234-5678-1234-56789abcdef1";
  static const String modeCharUuid = "12345678-1234-5678-1234-56789abcdef2";
  static const String statusCharUuid = "12345678-1234-5678-1234-56789abcdef3";

  @override
  void initState() {
    super.initState();
    checkPermissions();
    checkBluetoothState();
  }

  @override
  void dispose() {
    scanSubscription?.cancel();
    connectionSubscription?.cancel();
    batterySubscription?.cancel();
    super.dispose();
  }

  Future<void> checkBluetoothState() async {
    final adapterState = await FlutterBluePlus.adapterState.first;
    if (adapterState != BluetoothAdapterState.on) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text("Bluetooth Desactivado"),
            content: const Text("Por favor, activa el Bluetooth para usar TEARIS"),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("OK"),
              ),
            ],
          ),
        );
      }
    }
  }

  Future<void> checkPermissions() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.bluetooth,
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
      Permission.location,
    ].request();

    bool allGranted = statuses.values.every((status) => status.isGranted);
    
    if (!allGranted && mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text("Permisos Necesarios"),
          content: const Text(
            "TEARIS necesita permisos de Bluetooth y ubicación para funcionar correctamente."
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("OK"),
            ),
          ],
        ),
      );
    }
  }

  Future<void> scanForDevices() async {
    if (isScanning) return;

    setState(() {
      isScanning = true;
      scanResults.clear();
      connectionStatus = "Buscando dispositivos...";
    });

    try {
      await FlutterBluePlus.startScan(timeout: const Duration(seconds: 10));

      scanSubscription = FlutterBluePlus.scanResults.listen((results) {
        setState(() {
          scanResults = results.where((r) => 
            r.device.name.isNotEmpty && 
            (r.device.name.toLowerCase().contains('tearis') || 
             r.device.name.toLowerCase().contains('pi'))
          ).toList();
        });
      });

      await Future.delayed(const Duration(seconds: 10));
      await FlutterBluePlus.stopScan();
      
      setState(() {
        isScanning = false;
        if (scanResults.isEmpty) {
          connectionStatus = "No se encontraron auriculares TEARIS";
        } else {
          connectionStatus = "Selecciona tus auriculares";
        }
      });

      if (scanResults.isNotEmpty && mounted) {
        showDeviceListDialog();
      }
    } catch (e) {
      setState(() {
        isScanning = false;
        connectionStatus = "Error al buscar: $e";
      });
    }
  }

  void showDeviceListDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Dispositivos Encontrados"),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: scanResults.length,
            itemBuilder: (context, index) {
              final result = scanResults[index];
              return ListTile(
                leading: const Icon(Icons.headphones),
                title: Text(result.device.name),
                subtitle: Text(result.device.id.toString()),
                trailing: Text("${result.rssi} dBm"),
                onTap: () {
                  Navigator.pop(context);
                  connectToDevice(result.device);
                },
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancelar"),
          ),
        ],
      ),
    );
  }

  Future<void> connectToDevice(BluetoothDevice device) async {
    if (isConnecting) return;

    setState(() {
      isConnecting = true;
      connectionStatus = "Conectando a ${device.name}...";
    });

    try {
      await device.connect(timeout: const Duration(seconds: 15));
      
      connectedDevice = device;
      
      connectionSubscription = device.connectionState.listen((state) {
        if (state == BluetoothConnectionState.disconnected) {
          handleDisconnection();
        }
      });

      await discoverServices(device);
      
      setState(() {
        isConnecting = false;
        connectionStatus = "✅ Conectado a ${device.name}";
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Conectado exitosamente a ${device.name}"),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        isConnecting = false;
        connectionStatus = "❌ Error al conectar: $e";
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error: $e"),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> discoverServices(BluetoothDevice device) async {
    try {
      List<BluetoothService> services = await device.discoverServices();
      
      for (var service in services) {
        if (service.uuid.toString().toLowerCase() == tearisServiceUuid.toLowerCase()) {
          for (var characteristic in service.characteristics) {
            String charUuid = characteristic.uuid.toString().toLowerCase();
            
            if (charUuid == batteryCharUuid.toLowerCase()) {
              batteryCharacteristic = characteristic;
              await subscribeToBattery(characteristic);
            } else if (charUuid == modeCharUuid.toLowerCase()) {
              modeCharacteristic = characteristic;
            } else if (charUuid == statusCharUuid.toLowerCase()) {
              statusCharacteristic = characteristic;
            }
          }
        }
      }
    } catch (e) {
      debugPrint("Error discovering services: $e");
    }
  }

  Future<void> subscribeToBattery(BluetoothCharacteristic characteristic) async {
    try {
      await characteristic.setNotifyValue(true);
      
      batterySubscription = characteristic.value.listen((value) {
        if (value.isNotEmpty) {
          setState(() {
            batteryLevel = value[0];
          });
        }
      });

      final initialValue = await characteristic.read();
      if (initialValue.isNotEmpty) {
        setState(() {
          batteryLevel = initialValue[0];
        });
      }
    } catch (e) {
      debugPrint("Error subscribing to battery: $e");
    }
  }

  Future<void> sendModeCommand(String mode) async {
    if (modeCharacteristic == null) {
      showSnackBar("No conectado a los auriculares");
      return;
    }

    try {
      String command = "";
      switch (mode) {
        case "Escuela":
          command = "MODE_SCHOOL";
          break;
        case "Transporte":
          command = "MODE_TRANSPORT";
          break;
        case "Normal":
          command = "MODE_NORMAL";
          break;
      }

      await modeCharacteristic!.write(utf8.encode(command));
      
      setState(() {
        currentMode = mode;
      });

      showSnackBar("Modo $mode activado");
    } catch (e) {
      showSnackBar("Error al cambiar modo: $e");
    }
  }

  Future<void> disconnectDevice() async {
    if (connectedDevice == null) return;

    try {
      await connectedDevice!.disconnect();
      handleDisconnection();
      showSnackBar("Desconectado exitosamente");
    } catch (e) {
      showSnackBar("Error al desconectar: $e");
    }
  }

  void handleDisconnection() {
    setState(() {
      connectedDevice = null;
      batteryCharacteristic = null;
      modeCharacteristic = null;
      statusCharacteristic = null;
      connectionStatus = "Desconectado";
      batteryLevel = 0;
      currentMode = "Normal";
    });
    
    batterySubscription?.cancel();
    connectionSubscription?.cancel();
  }

  void showSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  Widget buildBatteryIndicator() {
    IconData batteryIcon;
    Color batteryColor;

    if (batteryLevel > 80) {
      batteryIcon = Icons.battery_full;
      batteryColor = Colors.green;
    } else if (batteryLevel > 50) {
      batteryIcon = Icons.battery_5_bar;
      batteryColor = Colors.lightGreen;
    } else if (batteryLevel > 30) {
      batteryIcon = Icons.battery_3_bar;
      batteryColor = Colors.orange;
    } else if (batteryLevel > 10) {
      batteryIcon = Icons.battery_2_bar;
      batteryColor = Colors.deepOrange;
    } else {
      batteryIcon = Icons.battery_1_bar;
      batteryColor = Colors.red;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: batteryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: batteryColor, width: 2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(batteryIcon, color: batteryColor, size: 32),
          const SizedBox(width: 12),
          Text(
            connectedDevice != null ? "$batteryLevel%" : "--",
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: batteryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildModeButton(IconData icon, String label, String mode, Color color) {
    final isActive = currentMode == mode && connectedDevice != null;
    
    return ElevatedButton.icon(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
        backgroundColor: isActive ? color : color.withOpacity(0.7),
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        elevation: isActive ? 8 : 4,
      ),
      icon: Icon(icon, size: 24),
      label: Column(
        children: [
          Text(label, style: const TextStyle(fontSize: 16)),
          if (isActive)
            const Text("ACTIVO", style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
        ],
      ),
      onPressed: connectedDevice != null ? () => sendModeCommand(mode) : null,
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("TEARIS - Control de Auriculares"),
        actions: [
          if (connectedDevice != null)
            IconButton(
              icon: const Icon(Icons.power_settings_new),
              tooltip: "Desconectar",
              onPressed: disconnectDevice,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Indicador de batería
            Center(child: buildBatteryIndicator()),
            
            const SizedBox(height: 30),
            
            // Estado de conexión
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: connectedDevice != null 
                    ? Colors.green.withOpacity(0.1)
                    : Colors.grey.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: connectedDevice != null ? Colors.green : Colors.grey,
                  width: 2,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    connectedDevice != null ? Icons.bluetooth_connected : Icons.bluetooth_disabled,
                    color: connectedDevice != null ? Colors.green : Colors.grey,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      connectionStatus,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),

            // Botón de búsqueda/conexión
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 20),
                backgroundColor: Colors.indigoAccent,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                elevation: 6,
              ),
              icon: isScanning 
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Icon(Icons.search, size: 28),
              label: Text(
                connectedDevice != null 
                    ? "Buscar otros dispositivos"
                    : isScanning 
                        ? "Buscando..." 
                        : "Buscar auriculares TEARIS",
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              onPressed: isScanning ? null : scanForDevices,
            ),

            const SizedBox(height: 40),
            
            const Divider(),
            const SizedBox(height: 20),

            // Título de modos
            const Text(
              "Modos de funcionamiento",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 20),

            // Botones de modos
            buildModeButton(Icons.volume_off, "Modo Normal", "Normal", Colors.blue),
            const SizedBox(height: 16),
            buildModeButton(Icons.school, "Modo Escuela", "Escuela", Colors.green),
            const SizedBox(height: 16),
            buildModeButton(Icons.directions_bus, "Modo Transporte", "Transporte", Colors.orange),

            const SizedBox(height: 40),

            // Información adicional
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? Colors.white.withOpacity(0.05) : Colors.black.withOpacity(0.05),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text("Modo actual:", style: TextStyle(fontSize: 14)),
                      Text(
                        currentMode,
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text("Tema:", style: TextStyle(fontSize: 14)),
                      Text(
                        isDark ? "Modo oscuro" : "Modo claro",
                        style: const TextStyle(fontSize: 14, fontStyle: FontStyle.italic),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}