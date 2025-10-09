#!/bin/bash
#
# TEARIS - Script de instalación para Raspberry Pi Zero 2 W
# Este script configura la Raspberry Pi como servidor BLE para los auriculares TEARIS
#

set -e

echo "======================================"
echo "TEARIS - Instalación en Raspberry Pi"
echo "======================================"
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor ejecuta este script como root (sudo)"
    exit 1
fi

# Actualizar el sistema
echo "📦 Actualizando el sistema..."
apt-get update
apt-get upgrade -y

# Instalar dependencias
echo "📦 Instalando dependencias..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-dbus \
    python3-gi \
    bluetooth \
    bluez \
    bluez-tools \
    libbluetooth-dev

# Instalar paquetes Python adicionales
echo "📦 Instalando paquetes Python..."
pip3 install dbus-python PyGObject

# Configurar Bluetooth
echo "🔧 Configurando Bluetooth..."

# Habilitar el servicio Bluetooth
systemctl enable bluetooth
systemctl start bluetooth

# Configurar el adaptador Bluetooth como discoverable
cat > /etc/bluetooth/main.conf << EOF
[General]
Name = TEARIS
Class = 0x000100
DiscoverableTimeout = 0

[Policy]
AutoEnable=true
EOF

# Crear directorio para el proyecto
echo "📁 Creando estructura de directorios..."
mkdir -p /opt/tearis
mkdir -p /opt/tearis/logs

# Copiar el servidor BLE (asume que tearis_server.py está en el directorio actual)
if [ -f "tearis_server.py" ]; then
    cp tearis_server.py /opt/tearis/
    chmod +x /opt/tearis/tearis_server.py
    echo "✅ Servidor BLE copiado"
else
    echo "⚠️  tearis_server.py no encontrado. Copia el archivo manualmente a /opt/tearis/"
fi

# Crear servicio systemd para autostart
echo "🔧 Creando servicio systemd..."
cat > /etc/systemd/system/tearis.service << EOF
[Unit]
Description=TEARIS BLE Server
After=bluetooth.service
Requires=bluetooth.service

[Service]
Type=simple
User=root
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 /opt/tearis/tearis_server.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/tearis/logs/tearis.log
StandardError=append:/opt/tearis/logs/tearis_error.log

[Install]
WantedBy=multi-user.target
EOF

# Hacer el dispositivo discoverable
echo "🔧 Configurando dispositivo como discoverable..."
cat > /opt/tearis/make_discoverable.sh << 'EOF'
#!/bin/bash
bluetoothctl << BTCTL
power on
discoverable on
pairable on
agent NoInputNoOutput
default-agent
BTCTL
EOF

chmod +x /opt/tearis/make_discoverable.sh

# Crear script de inicio
cat > /opt/tearis/start_tearis.sh << EOF
#!/bin/bash
/opt/tearis/make_discoverable.sh
sleep 2
python3 /opt/tearis/tearis_server.py
EOF

chmod +x /opt/tearis/start_tearis.sh

# Habilitar y arrancar el servicio
echo "🚀 Habilitando servicio TEARIS..."
systemctl daemon-reload
systemctl enable tearis.service

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "Para iniciar el servicio TEARIS:"
echo "  sudo systemctl start tearis.service"
echo ""
echo "Para ver el estado:"
echo "  sudo systemctl status tearis.service"
echo ""
echo "Para ver los logs:"
echo "  sudo journalctl -u tearis.service -f"
echo "  o"
echo "  tail -f /opt/tearis/logs/tearis.log"
echo ""
echo "El dispositivo se llamará 'TEARIS' en Bluetooth"
echo ""
echo "⚠️  IMPORTANTE: Reinicia la Raspberry Pi para aplicar todos los cambios"
echo "  sudo reboot"
echo ""
