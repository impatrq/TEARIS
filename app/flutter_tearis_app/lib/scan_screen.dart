import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({Key? key}) : super(key: key);

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  List<ScanResult> devicesList = [];

  @override
  void initState() {
    super.initState();
    startScan();
  }

  void startScan() {
    FlutterBluePlus.startScan(timeout: const Duration(seconds: 4));

    FlutterBluePlus.scanResults.listen((results) {
      setState(() {
        devicesList = results;
      });
    });
  }

  @override
  void dispose() {
    FlutterBluePlus.stopScan();
    super.dispose();
  }

  void connectToDevice(BluetoothDevice device) async {
    await device.connect();
    // Aquí podrías navegar a otra pantalla si lo deseas
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Conectado a ${device.name}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Buscar dispositivos')),
      body: ListView.builder(
        itemCount: devicesList.length,
        itemBuilder: (context, index) {
          final device = devicesList[index].device;
          return ListTile(
            leading: const Icon(Icons.headphones),
            title: Text(device.name.isNotEmpty ? device.name : 'Sin nombre'),
            subtitle: Text(device.id.toString()),
            trailing: ElevatedButton(
              child: const Text("Conectar"),
              onPressed: () => connectToDevice(device),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: startScan,
        child: const Icon(Icons.search),
      ),
    );
  }
}
