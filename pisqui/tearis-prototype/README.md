# TEARIS

Auriculares con inteligencia artificial para personas con Trastorno del Espectro Autista.

🎯 **Objetivo**  
Reducir la sobrecarga sensorial mediante la cancelación selectiva de sonidos molestos, manteniendo audibles las voces humanas y sonidos importantes.

🛠️ **Tecnologías utilizadas**
- ESP32: captura de sonido + filtros en tiempo real.
- Raspberry Pi Zero W: clasificación con modelo IA (TensorFlow Lite).
- Algoritmo FxLMS para cancelación activa de ruido.
- I2S, UART, C++, Python.

📂 **Estructura**
- `/hardware`: esquemas, conexiones y pinout.
- `/software/esp32`: código de captura y DSP.
- `/software/raspberry`: IA y control del sistema.
- `/modelo_IA`: dataset, entrenamiento y modelo exportado.
- `/docs`: manual técnico y documentación de pruebas.
- `/presentacion`: pitch en PDF, imágenes y video.

🧪 Proyecto final – IMPA TRQ 2025
