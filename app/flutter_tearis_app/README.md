# TEARIS - App Android

Aplicación móvil de control para auriculares TEARIS, diseñada para personas con hiperacusia.

## 📱 Características

- 🔗 Conexión Bluetooth Low Energy (BLE)
- 🔋 Monitoreo de batería en tiempo real
- 🎧 Control de 3 modos de funcionamiento
- 🌓 Tema claro/oscuro automático
- 🔄 Reconexión automática
- 📊 Indicadores visuales de estado
- 🎨 Interfaz Material Design 3

## 📋 Requisitos

- Flutter SDK 3.0 o superior
- Dart SDK 3.0 o superior
- Android Studio o VS Code con extensiones de Flutter
- Dispositivo Android:
  - **Mínimo**: Android 5.0 (API 21)
  - **Recomendado**: Android 12+ (API 31) para mejor BLE

## 🚀 Instalación

### 1. Instalar Flutter

Si no tienes Flutter instalado:

```bash
# macOS/Linux
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# Windows: Descargar desde https://flutter.dev
```

Verificar instalación:
```bash
flutter doctor
```

### 2. Clonar o crear el proyecto

```bash
# Crear nuevo proyecto
flutter create tearis
cd tearis

# O clonar repositorio existente
git clone <tu-repositorio>
cd tearis
```

### 3. Copiar archivos del proyecto

Estructura necesaria:
```
tearis/
├── lib/
│   └── main.dart                    # ← Copiar archivo proporcionado
├── android/
│   └── app/
│       └── src/
│           └── main/
│               └── AndroidManifest.xml  # ← Copiar archivo proporcionado
├── pubspec.yaml                     # ← Copiar archivo proporcionado
└── test/
    └── widget_test.dart             # ← Opcional
```

### 4. Instalar dependencias

```bash
flutter pub get
```

## ⚙️ Configuración

### Dependencias (pubspec.yaml)

```yaml
name: tearis
description: Aplicación de control para auriculares TEARIS

dependencies:
  flutter:
    sdk: flutter
  flutter_blue_plus: ^1.31.0      # Bluetooth Low Energy
  permission_handler: ^11.0.1      # Gestión de permisos
  cupertino_icons: ^1.0.2          # Iconos iOS

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
```

### Permisos Android (AndroidManifest.xml)

**Ubicación**: `android/app/src/main/AndroidManifest.xml`

Permisos incluidos:
- ✅ BLUETOOTH_SCAN (Android 12+)
- ✅ BLUETOOTH_CONNECT (Android 12+)
- ✅ BLUETOOTH_ADVERTISE (Android 12+)
- ✅ BLUETOOTH (Android <12)
- ✅ BLUETOOTH_ADMIN (Android <12)
- ✅ ACCESS_FINE_LOCATION (Android <12, para escaneo BLE)
- ✅ ACCESS_COARSE_LOCATION (Android <12, para escaneo BLE)

### Configuración build.gradle

**Archivo**: `android/app/build.gradle`

Verificar:
```gradle
android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.tearis"  // ← Personaliza esto
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
}
```

## 🔨 Compilación

### Modo Debug

```bash
# Ejecutar en dispositivo conectado
flutter run

# Compilar APK debug
flutter build apk --debug
```

### Modo Release

```bash
# APK release
flutter build apk --release

# App Bundle (para Google Play)
flutter build appbundle --release
```

### Salida de archivos

```bash
# APK
build/app/outputs/flutter-apk/app-release.apk

# App Bundle
build/app/outputs/bundle/release/app-release.aab
```

## 🧪 Pruebas

### Ejecutar tests

```bash
flutter test
```

### Test en dispositivo

```bash
# Ver dispositivos conectados
flutter devices

# Ejecutar en dispositivo específico
flutter run -d <device-id>
```

## 📱 Uso de la App

### Primera vez

1. **Instalar la app** en tu dispositivo Android
2. **Abrir TEARIS**
3. **Aceptar permisos**:
   - Bluetooth (requerido)
   - Ubicación (solo Android <12, para escaneo BLE)

### Conectar auriculares

1. **Presionar** "Buscar auriculares TEARIS"
2. **Esperar** el escaneo (aparecerá lista de dispositivos)
3. **Seleccionar** tu dispositivo TEARIS
4. **Esperar confirmación** "✅ Conectado a..."

### Funciones principales

#### 🔋 Monitoreo de batería
- Se actualiza automáticamente cada 10 segundos
- Indicador visual con colores:
  - 🟢 Verde: >80%
  - 🟡 Amarillo: 50-80%
  - 🟠 Naranja: 20-50%
  - 🔴 Rojo: <20%

#### 🎧 Modos de funcionamiento

**Modo Normal**
- Configuración balanceada
- Uso general diario

**Modo Escuela** 🏫
- Optimizado para escuchar voces
- Reduce ruido de fondo
- Ideal para clases, conferencias

**Modo Transporte** 🚌
- Máxima cancelación de ruido
- Reduce ruido de motores
- Ideal para buses, trenes, avión

#### ⚡ Desconectar
- Presionar botón de power en esquina superior derecha

## 🏗️ Arquitectura de la App

### Estructura de código

```dart
TearisApp (MaterialApp)
  └── TearisHome (StatefulWidget)
      ├── Estado de conexión BLE
      ├── Gestión de permisos
      ├── Escaneo de dispositivos
      ├── Conexión y desconexión
      ├── Suscripción a notificaciones
      └── UI components
```

### Componentes principales

**Estado**
- `connectedDevice`: Dispositivo BLE conectado
- `batteryLevel`: Nivel de batería (0-100)
- `connectionStatus`: Estado de conexión (texto)
- `currentMode`: Modo activo actual
- `isScanning`: Flag de escaneo activo

**Características BLE**
- Battery Characteristic: Lectura de batería
- Mode Characteristic: Envío de comandos de modo
- Status Characteristic: Estado del dispositivo

**UUIDs del servicio**
```dart
static const String tearisServiceUuid = "12345678-1234-5678-1234-56789abcdef0";
static const String batteryCharUuid = "12345678-1234-5678-1234-56789abcdef1";
static const String modeCharUuid = "12345678-1234-5678-1234-56789abcdef2";
static const String statusCharUuid = "12345678-1234-5678-1234-56789abcdef3";
```

## 🐛 Solución de Problemas

### Error: "flutter: command not found"

```bash
# Agregar Flutter al PATH
export PATH="$PATH:/ruta/a/flutter/bin"

# O en .bashrc / .zshrc
echo 'export PATH="$PATH:/ruta/a/flutter/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Error: "Android licenses not accepted"

```bash
flutter doctor --android-licenses
# Aceptar todas las licencias
```

### Error de importación en tests

**Problema**: `import 'package:TearisApp/main.dart';`

**Solución**:
```dart
// ❌ Incorrecto
import 'package:TearisApp/main.dart';

// ✅ Correcto
import '../lib/main.dart';
// o
import 'package:tearis/main.dart';  // Verificar nombre en pubspec.yaml
```

### La app no encuentra dispositivos

1. **Verificar permisos**:
   - Configuración → Apps → TEARIS → Permisos
   - Bluetooth: ✅
   - Ubicación: ✅ (Android <12)

2. **Verificar Bluetooth del teléfono**:
   - Bluetooth activado
   - Modo visible activado

3. **Verificar que los auriculares estén encendidos**

### La app se cierra al escanear

- Verificar que `AndroidManifest.xml` tenga todos los permisos
- Revisar logs: `flutter logs`
- Verificar versión de `flutter_blue_plus` en `pubspec.yaml`

### No se conecta después de encontrar dispositivo

- Verificar que el dispositivo BLE esté en modo pairable
- Reiniciar Bluetooth del teléfono
- Reiniciar la app

## 📊 Logs y Debug

### Ver logs en tiempo real

```bash
flutter logs
```

### Debug específico de BLE

```dart
// En main.dart, buscar:
logger.info('Mensaje de debug');

// Cambiar nivel de log si es necesario
```

### Logs de Android

```bash
# Ver logs del sistema
adb logcat | grep -i flutter
```

## 🎨 Personalización

### Cambiar nombre de la app

**En**: `android/app/src/main/AndroidManifest.xml`
```xml
<application
    android:label="TU_NOMBRE_AQUI"
    ...>
```

**En**: `pubspec.yaml`
```yaml
name: tu_nombre_app
```

### Cambiar colores

**En**: `lib/main.dart`
```dart
theme: ThemeData(
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),  // ← Cambiar color
),
```

### Cambiar icono

1. Agregar imagen en `assets/icon/icon.png`
2. Usar paquete `flutter_launcher_icons`:

```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.13.1

flutter_icons:
  android: true
  image_path: "assets/icon/icon.png"
```

3. Generar:
```bash
flutter pub get
flutter pub run flutter_launcher_icons
```

## 📦 Publicación

### Google Play Store

1. **Crear keystore**:
```bash
keytool -genkey -v -keystore ~/tearis-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias tearis
```

2. **Configurar signing**:

Crear `android/key.properties`:
```properties
storePassword=tu_password
keyPassword=tu_password
keyAlias=tearis
storeFile=/ruta/a/tearis-release-key.jks
```

3. **Editar** `android/app/build.gradle`:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    ...
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

4. **Compilar**:
```bash
flutter build appbundle --release
```

5. **Subir** a Google Play Console

## 🔐 Seguridad

- ✅ No se almacena información sensible
- ✅ Conexión BLE cifrada
- ✅ Sin acceso a internet (funciona offline)
- ✅ No se graba ni transmite audio
- ✅ Solo comandos de control por BLE

## 📄 Licencia

MIT License

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/NewFeature`)
3. Commit cambios (`git commit -m 'Add NewFeature'`)
4. Push a la rama (`git push origin feature/NewFeature`)
5. Abre un Pull Request

## 📞 Soporte

- Documentación completa del proyecto: Ver README.md principal
- Flutter docs: https://flutter.dev/docs

---

**TEARIS App** - Control de auriculares para hiperacusia  
Versión 1.0 | Flutter 3.0+ | Android 5.0+

Hecho con ❤️ para personas con hiperacusia 🎧
