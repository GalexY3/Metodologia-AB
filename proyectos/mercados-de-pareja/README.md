# Mercados de pareja · acceso estable

**Estado de investigación comprobado el 30/10/2026.** Este directorio en `main` es una entrada documental, **no** una fusión del historial experimental. La historia técnica, los contratos, fuentes y resultados siguen en ramas de investigación independientes.

## Ruta activa de N257–N276
- Rama: [research/ab-h-esbm-event-parity-n257-n276-20261030](https://github.com/GalexY3/Metodologia-AB/tree/research/ab-h-esbm-event-parity-n257-n276-20261030/proyectos/mercados-de-pareja).
- Punto de partida autorizado y comprobado: `28ee845cca88e16f13f25962e4b103335484d9a1`; su [planificación no ejecutada](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-event-parity-n257-n276-20261030/proyectos/mercados-de-pareja/research/ABH_N257_N276_20261030/PREPARATION_NOT_EXECUTED.md).
- [Tareas para Codex](tareas_codex/README.md) (índice en main, con tareas de recuperación, SIGSEGV, timeout y paridad individual).

## Evidencia y límites
- [Cierre N237–N256](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-polynomial-blossom-n237-n256-20261030/proyectos/mercados-de-pareja/research/ABH_N237_N256_20261030/REPORT.md), HEAD `7307f81174dab5050bf3f28f04235e7dc6666e74`.
- 20/20 ejecuciones históricas: 18 PASS técnicos y dos fallos adversariales preservados; 60/60 coincidencias de métricas/series agregadas de simulaciones N144 T16 K7, **no** identidad de eventos ni parejas por individuo.
- N242: SIGSEGV C++ en grafo n143. N246: timeout 12s en n144 casi completo.
- Falta recuperar `ESBM_ABH_N237_N256_Blossom_60corridas.zip` (SHA256 `349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c`) para reproducir los fallos con instrumentos originales.
- N257–N276: **20 autorizados, 0 ejecutados, 20 disponibles** en el último estado aquí registrado; comprobar la rama activa antes de asumir vigencia.
- **CT2 científico 7/100; STOP_R5 humano activo.** Ninguna evidencia humana nueva ni validación causal.
- ESBM original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` y SRC104 sin modificaciones.

## Política de publicación
Los archivos estables de navegación y las tareas autorizadas pueden entrar en `main` por commits documentales independientes. Código experimental, métricas, evaluaciones negativas y reparaciones deben permanecer en ramas con prerregistro/ledger y evidencia intacta hasta una revisión explícita; no hacer fusión masiva de historiales divergentes. No SSJY; no aceptar licencias; no contactar autores; no CI costosa.

**No utilizar este README como prueba de ejecución de nuevos ciclos.**
