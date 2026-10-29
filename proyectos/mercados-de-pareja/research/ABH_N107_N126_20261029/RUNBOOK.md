# Reproducción y portabilidad — AB-H ESBM N107–N126

**Archivo de datos:** exclusivamente simulaciones artificiales de agentes, ningún registro humano original. **Fuente de verdad versionada:** [informe y ledger](REPORT.md), cuatro `PREREG_BLOCK_{A,B,C,D}.json` y cuatro `LEDGER_BLOCK_{A,B,C,D}.json`.

**Entorno usado en ejecución:** Python 3.13.5, NumPy 2.3.5, NetworkX 3.6.1. Se verificó compilación y ejecución aislada en directorio temporal con las librerías **ya instaladas** en el mismo entorno. No se ha verificado un contenedor limpio sin dependencias ni un sistema operativo independiente.

**Código ejecutado:** `esbm_schedule_adapter.py`, `esbm_schedule_adapter_v3.py`, `small_fixture.py` y seis runners `cycle_runner_a.py`, `cycle_runner_a_repair.py`, `cycle_runner_b.py`, `cycle_runner_c.py`, `cycle_runner_c_repair.py`, `cycle_runner_d.py`. Los archivos Git blob se compararon byte a byte con los archivos locales efectivamente ejecutados. El código histórico original permanece en `../ABR_ESBM20_20261028/esbm_dynamic.py` con **SHA256** `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.

**Preparación de un clon:** copiar el original histórico `esbm_dynamic.py` **sin editarlo** al directorio de trabajo junto a los archivos de este lote, después de verificar su checksum. Instalar NumPy/NetworkX de las versiones citadas en un entorno virtual. Ejemplos para POSIX, ejecutados desde este directorio:
```bash
cp ../ABR_ESBM20_20261028/esbm_dynamic.py ./esbm_dynamic.py
sha256sum esbm_dynamic.py
python -m pip install numpy==2.3.5 networkx==3.6.1
python -c "import esbm_schedule_adapter as a; print(a.SOURCE_SHA256)"
python cycle_runner_d.py
```

**Importante:** no ejecutar las baterías iniciales completas `cycle_runner_a.py` o `cycle_runner_c.py` sin límite temporal: sus versiones originales excedieron el presupuesto con grafo denso N144 o dos slots. Consultar `N108_REPAIR_PREREG.md`, `N110_N111_REPAIR_PREREG.md` y `N120_N121_REPAIR_PREREG.md` y utilizar los runners reparados o seleccionar las funciones exitosas. Los resultados de pruebas menores están conservados en `RESULTS_N*.json` y en el paquete ZIP adjunto al informe de ChatGPT que incluye **ocho recibos JSON completos** y un `MANIFEST_SHA256.json`. El ZIP **no** está cargado a GitHub; no inventar su URL de GitHub.

**Criterios de aceptación:** N107 igualdad exacta de 60 diccionarios con ESBM v2 original; N108 integridad de 144 conjuntos de riesgo tras reparación top4; N113 dos shams longitudinales idénticos; N118 seis trayectorias de una ronda idénticas a v3; N124 18 checks de relabel; N125 tres rechazos fail-closed; N126 mismo entorno/proceso aislado en directorio limpio. Consultar ledger por objetivos, seeds, fuentes, incidentes y alcance. El adaptador es una transformación controlada de fuente Python con checksum original; no ejecutar sobre archivos externos no confiables ni presentarlo como API estable.

**Estado científico:** originalidad y derechos humanos `STOP_R5`, CT2 ordinal 7/100, madurez técnica ponderada 42.20 % auditada. El bootstrap post hoc `POST_HOC_PAIRED_SEED_AUDIT.md` es auxiliar y **no consume ciclo**. Sin replicación externa humana, sin nuevas fuentes con licencia verificada.
