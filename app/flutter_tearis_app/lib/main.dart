import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

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
  String connectionStatus = "Desconectado";

  Future<void> connectToEarphones() async {
    setState(() {
      connectionStatus = "Buscando auriculares...";
    });

    try {
      await FlutterBluePlus.startScan(timeout: const Duration(seconds: 4));

      FlutterBluePlus.scanResults.listen((results) async {
        for (var result in results) {
          if (result.device.name == "NOMBRE_DEL_AURICULAR") {
            await FlutterBluePlus.stopScan();

            try {
              await result.device.connect();
              setState(() {
                connectionStatus = "✅ Conectado a ${result.device.name}";
              });
            } catch (e) {
              setState(() {
                connectionStatus = "❌ Error al conectar";
              });
            }
            break;
          }
        }
      });
    } catch (e) {
      setState(() {
        connectionStatus = "❌ Error en el escaneo";
      });
    }
  }


  Widget buildButton(IconData icon, String label, VoidCallback onPressed) {
    return ElevatedButton.icon(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
        backgroundColor: Colors.indigoAccent.withOpacity(0.9),
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        elevation: 4,
      ),
      icon: Icon(icon, size: 24),
      label: Text(label, style: const TextStyle(fontSize: 16)),
      onPressed: onPressed,
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Bienvenid@ a Tearis"),
        actions: [
          const Icon(Icons.headphones, size: 30),
          IconButton(
            icon: const Icon(Icons.power_settings_new),
            tooltip: "Apagar auriculares",
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Auriculares apagados")),
              );
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: const [
                  Text("100%", style: TextStyle(fontSize: 18)),
                  SizedBox(width: 20),
                  Icon(Icons.battery_4_bar_rounded),
                ],
              ),
            ),
            const SizedBox(height: 40),
            buildButton(Icons.hearing, "Encontrar auriculares", () {
              connectToEarphones();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Buscando auriculares...")),
              );
            }),
            const SizedBox(height: 20),
            buildButton(Icons.school, "Modo Escuela", () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Modo escuela activad0")),
              );
            }),
            const SizedBox(height: 20),
            buildButton(Icons.emoji_transportation, "Modo transporte", () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Modo transporte activado")),
              );
            }),
            const Spacer(),
            Center(
              child: Column(
                children: [
                  Text(
                    connectionStatus,
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isDark ? "Modo oscuro" : "Modo claro",
                    style: const TextStyle(fontSize: 14, fontStyle: FontStyle.italic),
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

