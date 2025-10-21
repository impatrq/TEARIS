#include <iostream>
#include <vector>
#include <cmath>
#include <alsa/asoundlib.h>
#include "Iir.h"

// Corrected function signature for the ALSA error handler
static void alsa_error_handler(const char *file, int line, const char *function, int err, const char *fmt, ...) {
    // This handler simply ignores the errors.
}

int main() {
    // --- Configuración de ALSA ---
    snd_pcm_t *handle_in, *handle_out;
    int err;
    unsigned int rate = 16000;      // Frecuencia de muestreo de 16 kHz
    unsigned int channels = 2;      // 2 canales (estéreo)
    int format = SND_PCM_FORMAT_S32_LE; // Formato S32_LE
    
    // Desactiva los mensajes de error de ALSA para una salida más limpia
    snd_lib_error_set_handler(alsa_error_handler);

    // Abrir dispositivo de captura (input)
    if ((err = snd_pcm_open(&handle_in, "default", SND_PCM_STREAM_CAPTURE, 0)) < 0) {
        std::cerr << "Error al abrir el dispositivo de captura: " << snd_strerror(err) << std::endl;
        return 1;
    }

    // Abrir dispositivo de reproducción (output)
    if ((err = snd_pcm_open(&handle_out, "default", SND_PCM_STREAM_PLAYBACK, 0)) < 0) {
        std::cerr << "Error al abrir el dispositivo de reproducción: " << snd_strerror(err) << std::endl;
        snd_pcm_close(handle_in);
        return 1;
    }

    // Configurar parámetros de entrada
    if ((err = snd_pcm_set_params(handle_in, (snd_pcm_format_t)format, SND_PCM_ACCESS_RW_INTERLEAVED, channels, rate, 1, 500000)) < 0) {
        std::cerr << "Error en la configuración del dispositivo de captura: " << snd_strerror(err) << std::endl;
        snd_pcm_close(handle_in);
        snd_pcm_close(handle_out);
        return 1;
    }

    // Configurar parámetros de salida
    if ((err = snd_pcm_set_params(handle_out, (snd_pcm_format_t)format, SND_PCM_ACCESS_RW_INTERLEAVED, channels, rate, 1, 500000)) < 0) {
        std::cerr << "Error en la configuración del dispositivo de reproducción: " << snd_strerror(err) << std::endl;
        snd_pcm_close(handle_in);
        snd_pcm_close(handle_out);
        return 1;
    }

    // --- Configuración del Filtro IIR ---
    const int order = 4;
    Iir::Butterworth::LowPass<order> lowpass_filter;
    // Frecuencia de corte de 1 kHz, puedes cambiarla
    const float cutoff_frequency = 1000;
    
    lowpass_filter.setup(static_cast<double>(rate), static_cast<double>(cutoff_frequency));
    
    std::cout << "Iniciando filtrado en tiempo real..." << std::endl;
    std::cout << "Frecuencia de muestreo: " << rate << " Hz" << std::endl;
    std::cout << "Frecuencia de corte del filtro: " << cutoff_frequency << " Hz" << std::endl;
    
    // Búfer para leer y escribir muestras, ahora de 32 bits (int)
    const int buffer_size = 256;
    std::vector<int> buffer(buffer_size * channels); // Ajustar el tamaño para 2 canales

    // --- Bucle de procesamiento ---
    while (true) {
        // Leer del micrófono (entrada)
        err = snd_pcm_readi(handle_in, buffer.data(), buffer_size);
        if (err < 0) {
            if (err == -EPIPE) {
                std::cerr << "Desbordamiento de búfer. Se reinicia el stream." << std::endl;
                snd_pcm_prepare(handle_in);
            } else {
                std::cerr << "Error de lectura: " << snd_strerror(err) << std::endl;
                break;
            }
        } else if (err != buffer_size) {
            // Manejar lecturas incompletas si es necesario
        }

        // Procesar cada muestra del búfer (nota: hay dos canales, por eso el bucle va de 2 en 2)
        for (int i = 0; i < buffer.size(); ++i) {
            float sample_float = static_cast<float>(buffer[i]) / 2147483648.0f; // Conversión a float (2^31)
            sample_float = lowpass_filter.filter(sample_float); // Aplicar filtro
            buffer[i] = static_cast<int>(sample_float * 2147483648.0f); // Conversión de vuelta a 32-bit
        }
        
        // Escribir en el altavoz (salida)
        err = snd_pcm_writei(handle_out, buffer.data(), buffer_size);
        if (err < 0) {
            if (err == -EPIPE) {
                std::cerr << "Subdesbordamiento de búfer. Se reinicia el stream." << std::endl;
                snd_pcm_prepare(handle_out);
            } else {
                std::cerr << "Error de escritura: " << snd_strerror(err) << std::endl;
                break;
            }
        } else if (err != buffer_size) {
            // Manejar escrituras incompletas
        }
    }

    // Limpiar
    snd_pcm_close(handle_in);
    snd_pcm_close(handle_out);

    return 0;
}
