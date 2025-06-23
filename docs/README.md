
# TEARIS 🚀

**Auriculares con cancelación selectiva de ruido para personas con TEA y sensibilidad auditiva**

---

## 🎯 Introducción

TEARIS (TEA + auris, latín: oído) es un sistema innovador de auriculares con **cancelación activa de ruido adaptativa**, creado para personas con Trastorno del Espectro Autista (TEA), PTSD, fibromialgia, migrañas crónicas y otras condiciones con hipersensibilidad auditiva. El dispositivo filtra sonidos estridentes y molestos, mientras preserva voces humanas, alarmas y otros sonidos críticos, mejorando significativamente la calidad de vida y facilitando la inclusión educativa y social.

---

## 🛠️ Características destacadas

- **Cancelación inteligente de ruido** gracias a un modelo de Machine Learning embebido (TensorFlow Lite).
- **Microcontrolador Raspberry Pi Zero 2 W** y kernel RT-Linux para procesamiento en tiempo real (< 20 ms).
- **Algoritmo FxLMS** para generación de onda inversa y atenuación precisa.
- **Modos configurables (“Aula”, “Transporte”, etc.)** mediante app móvil.
- **Micrófonos INMP441 direccionales**, módulo Bluetooth CSR4.0 y tarjeta de sonido USB.
- **Diseño ergonómico y liviano** con carcasa impresa en 3D.
- **Autonomía de hasta 6 horas** con batería recargable de 2.000 mAh.
- **App móvil para personalización de filtros y perfiles**, en desarrollo.

---

## 🧩 Beneficios e impacto

- 🔹 **Reducción de estrés y crisis sensoriales**, favoreciendo la concentración.
- 🔹 **Inclusión escolar**, permitiendo a estudiantes con TEA rendir mejor en entornos ruidosos.
- 🔹 **Autonomía en espacios públicos** como transporte, comercios y hospitales.
- 🔹 **Escalable y accesible**, con costo estimado de USD 150 y posibilidad de colaboración con ONGs, escuelas y salud pública.

---

## 🧠 Arquitectura del sistema

```text
[ Micrófonos ➝ Raspberry Pi Zero W (ANC+ML) ➝ Auriculares ]
       ⬆⬇          ⬆                  ⬇
     Sonido       Procesamiento       Onda inversa
                    + App móvil
````

* Captura: micrófonos INMP441.
* Procesado: Raspberry Pi + TensorFlow Lite + FxLMS.
* Control: kernel de tiempo real.
* Reproducción: auriculares + Bluetooth.
* Energía: batería y gestión integrada.

---

## 🧪 Instalación y uso (prototipo)

```bash
git clone https://github.com/tu-usuario/tearis.git
cd tearis

# (Ejemplos de instalación)
pip install -r requirements.txt
# Compilación de firmware y carga en la Raspberry Pi
# Configuración de RT-Linux + deploy de modelos ML
```

Próximamente: **versión alfa de app móvil**, enlaces de descarga y documentación detallada.

---

## 👥 Equipo

Desarrollado en el Taller Regional Quilmes – E.E.T. Nº 7, Especialidad Aviónica:

* Tomás M. Bianco
* Luis Britez
* Santino R. Ramírez Tolosa
* Juan C. Somoza 

---

## 💰 Costos estimados

| Componente            |           Precio aprox. USD |
| --------------------- | --------------------------: |
| Micrófonos INMP441    |                          20 |
| Raspberry Pi Zero 2 W |                          20 |
| Carcasa + soportes    |                          15 |
| Tarjeta de audio USB  |                          15 |
| Bluetooth CSR 4.0     |                          15 |
| Batería 2.000 mAh     |                          12 |
| Cables y conectores   |                           5 |
| **Total estimado**    | **150 USD** (\~ARS 183.000) |

Financiado mediante cooperadora escolar, equipo propio y sponsors.

---

## 🛠️ Roadmap

1. Prototipo funcional y pruebas iniciales.
2. Ajuste de filtros y perfiles según feedback.
3. Lanzamiento de app móvil beta.
4. Validación con usuarios reales en escuelas.
5. Optimización energética y ergonomía.
6. Búsqueda de socios estratégicos (ONGs, salud, educación).

---

## 🎉 Contribuciones

¡Sumate! Tu ayuda puede incluir:

* Mejora y validación del ML.
* Diseño de carcasa y ergonomía.
* Desarrollo y testing de la app.
* Diseño, pruebas de hardware y PCB.

Consulta el archivo [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.


---

## 🔗 Referencias

* Autismo y sobrecarga sensorial (Ministerio de Salud Argentina)
* Estudios de misofonía y sensorialidad
* Soluciones similares en ANC adaptativo

---
---

**TEARIS no es solo tecnología, es inclusión.** 🚀

```
