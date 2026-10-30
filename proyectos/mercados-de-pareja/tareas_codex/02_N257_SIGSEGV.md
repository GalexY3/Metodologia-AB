# Tarea Codex 02 · N257: depuración adversarial del SIGSEGV N242

**Dependencia:** tarea 01 completa y fixture/código original de N242 `PRESENT_AND_HASH_VERIFIED` o regeneración idéntica SHA verificada. Sin ello, `BLOCKED_MISSING_FIXTURE`: no ejecutar ni consumir N257 como reproducción del error histórico.

**Objetivo:** discriminar si el `SIGSEGV -11` del backend C++ Boost n143 se origina en parser/protocolo, construcción del grafo, aritmética de pesos, optimizador Boost, ABI/entorno o defecto de la instrumentación. Comparador competente: NetworkX con mismo grafo y objetivo lexicográfico cardinalidad/peso; controles pequeños y n144 del lote previo sin fingir independencia estadística.

**Prerequisitos ABSOLUTOS antes de outcome:**
- Contrato **A–J** completo con falsadores predefinidos; congelar código del runner, C++ idéntico, copias instrumentadas, generador/fixture, versiones y todos los SHA en commit previo.
- Predeterminación de seeds, límites de CPU/RAM/tiempo, regla de STOP, política para fallos y registro de primer grafo fallido. No cambiar librería o parser entre intentos sin nuevo freeze.

**Ejecución condicionada:**
1. Reproducir baseline con fixture idéntico; guardar código retorno, stderr, stdout, input SHA, tiempo y RSS; no ocultar fallo.
2. Compilar la MISMA fuente con flags de depuración y ASan/UBSan (registrar versiones exactas y flags); distinguir reproducción de comportamiento bajo compilación instrumentada.
3. Obtener stack trace; aplicar minimización delta-debugging sólo sobre una COPIA del fixture y etiquetar el resultado como diagnóstico, nunca como el test original.
4. Validar cardinalidad/peso con cálculo independiente; tratar óptimos múltiples como equivalentes en objetivo pero no como igualdad de aristas individuales.
5. Si se propone reparación, escribir nuevo prereg/commit SHA antes de probar la versión reparada. Preservar el primer resultado negativo y el binario pre-reparación.

**Cierre:** recibos crudos, ledgers A–J, oráculos/control adversarial, resultado PASS/FAIL/BLOCKED y causa solo si demostrada; mantener CT2 científico 7/100 sin evidencia humana nueva. **Un ciclo N257 válido exige ejecución efectiva**; no contabilizar preparación.