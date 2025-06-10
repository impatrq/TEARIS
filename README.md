# TEARIS
**Tecnología de Exclusión Auditiva Relevante e Inteligente Selectiva**
El sistema TEARIS integra distintas tecnologías modernas para lograr una cancelación de ruido selectiva, adaptable y eficiente:

🎧 Cancelación Activa de Ruido (ANC)
La tecnología ANC se basa en el principio de interferencia destructiva: micrófonos captan el sonido ambiente, el sistema genera una señal con fase invertida y esta se reproduce para cancelar las ondas sonoras no deseadas. En TEARIS, este proceso se adapta dinámicamente para priorizar frecuencias problemáticas como gritos, bocinas o motores.

Se utilizarán micrófonos omnidireccionales combinados con un procesador de señales digitales (DSP) o un microcontrolador con capacidades de audio en tiempo real.

🧠 Clasificación de Sonidos con Machine Learning
TEARIS incorpora un modelo de aprendizaje automático entrenado para clasificar tipos de sonidos en tiempo real. El modelo puede distinguir entre:

Voz humana (docentes, compañeros, padres)

Sonidos relevantes (alarmas, timbres, anuncios)

Sonidos intrusivos (tráfico, gritos, conversaciones superpuestas)

Para esto, se utilizará un enfoque basado en redes neuronales (como CNNs o modelos de audio tipo YAMNet) entrenados con datasets de sonido urbano, escolar y doméstico. Los sonidos captados se transforman en espectrogramas y se evalúan en tiempo real para decidir si deben ser bloqueados o permitidos.

📱 App Móvil Personalizable
Se desarrollará una app móvil (Flutter o React Native) conectada a los auriculares vía Bluetooth Low Energy (BLE). Esta permitirá al usuario o su cuidador:

Ajustar la sensibilidad del filtro de sonidos

Elegir perfiles de entorno (aula, transporte, hogar)

Visualizar estadísticas de uso o eventos sonoros

Actualizar firmware del dispositivo

Además, se podrá personalizar qué sonidos permitir y cuáles bloquear, lo que da control total sobre la experiencia auditiva.

⏱️ Procesamiento en Tiempo Real
Para garantizar una experiencia fluida y sin demoras, TEARIS empleará procesamiento de señal optimizado en microcontroladores como ESP32 o Raspberry Pi Pico con módulos de audio dedicados. Se evaluarán opciones de hardware con soporte para procesamiento paralelo o incluso unidades de aceleración de IA (como el Google Edge TPU si fuera necesario).


INTEGRANTES:
Britez Luis
Tolosa Santino
Somoza Juan Cruz
Bianco Tomas
