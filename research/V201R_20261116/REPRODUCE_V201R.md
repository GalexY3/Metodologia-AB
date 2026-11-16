# Reproducir la auditoría V201-R

Auditoría matemática posterior a una propuesta proporcionada por el investigador. No es una campaña MARL preregistrada ni una réplica científica externa. No requiere GPU ni un servicio externo.

El texto científico de entrada es `theory_inputs/HYDROGEN_V201R_20261116/HYDROGEN_V201R_RECONSTRUCTION.txt`, SHA-256 `82592df070764a5889df4227536fd24bdaf935512de5965aa02aa77197eda411`. Los parámetros se transcriben explícitamente en el código; el texto se conserva para auditar esa transcripción. No se descargan artículos ni datos humanos al reproducir.

Entorno usado: Python 3.12, NumPy, Numba y Matplotlib del entorno local del proyecto. `research_resource_limits.py` aplica dos hilos de Numba a los controles principales, prioridad BelowNormal y seis procesadores lógicos de afinidad en Windows. No fija por separado todos los hilos de BLAS. La salida imprime los límites realmente aplicados. Las versiones exactas constan en el ledger. El helper de afinidad está adaptado a este ordenador; en otro hardware hay que registrar cualquier ajuste necesario.

Desde el directorio que contiene los scripts y los resultados originales:

```powershell
& 'C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe' -X utf8 '.\reproduce_v201r.py' --destination 'C:\Programación\AB_reproductions\V201R_theory_20261116'
```

Se exige un destino nuevo. El programa copia las fuentes necesarias, ejecuta los seis pasos y compara todos los valores de los seis JSON científicos con los originales. No borra carpetas, modifica el índice Git ni vuelve a entrenar agentes. Para otra máquina se adapta la ruta del intérprete y el destino; se conservan los mismos scripts y entrada. Una diferencia numérica entre plataformas debe investigarse y documentarse, no borrarse automáticamente.

Orden de ejecución:

1. `v201r_theory_precheck.py`: probabilidades, incentivos y ambigüedades de la propuesta.
2. `v201r_single_agent_bellman.py`: control autárquico individual y salida a tierra nueva garantizada.
3. `v201r_capital_coalition_audit.py`: testigos de inversión conjunta y desviaciones.
4. `v201r_relational_certificate.py`: intervalos racionales del juego reparado con capital fijo y observación pública.
5. `audit_v201r_capital_bounds.py`: algoritmo optimista independiente para la cota de inversión individual.
6. `analyze_v201r_controls.py`: síntesis, ejemplo de castigo no creíble y figura.

Los primeros scripts protegen sus salidas frente a sobrescritura. Los borradores y el primer intento fallido del análisis original están preservados como tales, separados de los resultados vigentes. No se deben usar los campos antiguos de pivotalidad de un borrador como prueba de equilibrio.

El certificado público impone la estrategia contingente y fija capital, identidades, roles y pérdidas. La reproducción no transforma ese control en institución aprendida ni establece una banda dinámica de depreciación. Los PDFs de terceros se consultaron como antecedentes y no forman parte de la distribución reproducible.
